from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from safetensors.torch import load_file
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
import time
from enum import Enum
from typing import Optional
import io
import base64
import gc

# ONNX Runtime 관련 임포트
import onnxruntime as ort
from diffusers.pipelines.stable_diffusion import StableDiffusionOnnxPipeline
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import StableDiffusionPipeline
from diffusers.schedulers.scheduling_dpmsolver_multistep import DPMSolverMultistepScheduler
from diffusers import OnnxStableDiffusionPipeline
from PIL import Image
from diffusers.schedulers.scheduling_euler_ancestral_discrete import EulerAncestralDiscreteScheduler
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline

# 환경 변수 로드
load_dotenv()

class ModelType(str, Enum):
    SD15 = "SD1.5"
    SDXL = "SDXL"

class LoRAStyle(str, Enum):
    NONE = "none"
    KOREAN = "Korean-doll-likeness"
    JAPANESE = "Japanese-doll-likeness"
    TAIWANESE = "Taiwan-doll-likeness"
    SURREAL = "surreal_landscape"
    LCM = "LCMTurboMix_Euler_A_fix"
    ANIMAL = "zhibi-sdxl"

app = FastAPI(title="Stable Diffusion Image Generator API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 이미지 저장 디렉토리 설정
IMAGES_DIR = Path("generated_images")
IMAGES_DIR.mkdir(exist_ok=True)

# 모델 초기화
sd15_model_id = "runwayml/stable-diffusion-v1-5"
sdxl_model_id = "stabilityai/stable-diffusion-xl-base-1.0"
pipe = None

# LoRA 모델 설정
MODELS_DIR = Path("models")
HELLOWORLD_LORA = "leosamsHelloworldXL_helloworldXL70"
current_lora_style = None
current_scheduler = None
current_model_type = None

def get_model_type(style: LoRAStyle) -> ModelType:
    """스타일에 따른 모델 타입 반환"""
    # HelloworldXL은 항상 사용되므로 모든 스타일에 SDXL 사용
    return ModelType.SDXL

def check_lora_file(lora_path: str, name: str) -> None:
    """LoRA 파일 유효성 검사"""
    if not os.path.exists(lora_path):
        raise FileNotFoundError(f"{name} LoRA 파일을 찾을 수 없습니다: {lora_path}")
    
    if not lora_path.endswith('.safetensors'):
        raise ValueError(f"{name} LoRA 파일이 safetensors 형식이 아닙니다: {lora_path}")
    
    file_size = os.path.getsize(lora_path)
    if file_size == 0:
        raise ValueError(f"{name} LoRA 파일이 비어있습니다: {lora_path}")

def load_lora_weights(pipe, model_dir: str, weight_name: str, adapter_name: str, weight: float | None = None) -> None:
    """LoRA 가중치 로드 및 상세 에러 처리"""
    try:
        kwargs = {
            "weight_name": weight_name,
            "adapter_name": adapter_name
        }
        if weight is not None:
            kwargs["weight"] = str(weight)  # weight를 문자열로 변환
            
        pipe.load_lora_weights(model_dir, **kwargs)
    except ValueError as e:
        if "Invalid LoRA checkpoint" in str(e):
            raise ValueError(
                f"LoRA 체크포인트가 유효하지 않습니다. "
                f"이 LoRA({weight_name})가 현재 모델(SDXL)과 호환되는지 확인해주세요."
            )
        elif "layer" in str(e).lower() and "not found" in str(e).lower():
            raise ValueError(
                f"LoRA 파일의 레이어가 현재 모델과 맞지 않습니다. "
                f"이 LoRA({weight_name})가 SDXL용인지 확인해주세요."
            )
        raise
    except Exception as e:
        if "cuda" in str(e).lower():
            raise RuntimeError(f"CUDA 관련 오류가 발생했습니다: {e}")
        elif "memory" in str(e).lower():
            raise RuntimeError(f"메모리 부족 오류가 발생했습니다: {e}")
        raise RuntimeError(f"LoRA 로드 중 알 수 없는 오류가 발생했습니다: {e}")

def initialize_model(style: LoRAStyle = LoRAStyle.NONE):
    global pipe, current_lora_style, current_scheduler, current_model_type
    
    model_type = get_model_type(style)
    
    # 이미 같은 스타일이 로드되어 있다면 재사용
    if current_lora_style == style and pipe is not None:
        return
    
    # 이전 파이프라인 정리
    if pipe is not None:
        del pipe
        gc.collect()
    
    try:
        # SDXL 모델 로드
        pipe = StableDiffusionXLPipeline.from_pretrained(
            sdxl_model_id,
            torch_dtype=torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        ).to("cpu")
        
        # CPU 최적화 설정
        pipe.enable_attention_slicing(slice_size=1)
        
        # 스케줄러 설정
        if style == LoRAStyle.LCM:
            pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
                pipe.scheduler.config,
                use_karras_sigmas=True
            )
            current_scheduler = "euler_a"
        else:
            pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                pipe.scheduler.config,
                use_karras_sigmas=True
            )
            current_scheduler = "dpm"
        
        # HelloworldXL LoRA 적용 (필수)
        helloworld_path = str(MODELS_DIR / f"{HELLOWORLD_LORA}.safetensors")
        check_lora_file(helloworld_path, "HelloworldXL")
        
        try:
            load_lora_weights(
                pipe=pipe,
                model_dir=str(MODELS_DIR),
                weight_name=f"{HELLOWORLD_LORA}.safetensors",
                adapter_name="helloworld"
            )
            print(f"HelloworldXL LoRA 로드 완료")
        except Exception as e:
            print(f"HelloworldXL LoRA 로드 중 오류 발생")
            raise
        
        # 추가 LoRA 모델 적용 (선택)
        if style != LoRAStyle.NONE:
            lora_path = str(MODELS_DIR / f"{style}.safetensors")
            if os.path.exists(lora_path):
                try:
                    check_lora_file(lora_path, str(style))
                    
                    weight = 0.9 if style == LoRAStyle.LCM else 0.6
                    load_lora_weights(
                        pipe=pipe,
                        model_dir=str(MODELS_DIR),
                        weight_name=f"{style}.safetensors",
                        adapter_name="additional",
                        weight=weight
                    )
                    print(f"{style} LoRA 로드 완료")
                except Exception as e:
                    print(f"경고: {style} LoRA 로드 중 오류 발생: {e}")
                    print("기본 HelloworldXL LoRA만 사용하여 계속 진행합니다.")
                    
        current_lora_style = style
        current_model_type = model_type
        print(f"모델 초기화 완료: SDXL + HelloworldXL + {style}, 스케줄러: {current_scheduler}")
        
    except Exception as e:
        print(f"모델 초기화 중 오류 발생: {e}")
        raise

def cleanup_old_images():
    """1시간 이상 된 이미지 파일 삭제"""
    current_time = time.time()
    for image_file in IMAGES_DIR.glob("*.png"):
        if image_file.stat().st_mtime < (current_time - 3600):  # 1시간
            try:
                image_file.unlink()
            except Exception as e:
                print(f"이미지 삭제 중 오류 발생: {e}")

@app.post("/generate")
async def generate_image(
    prompt: str = Form(...),
    style: LoRAStyle = Form(LoRAStyle.NONE),
    negative_prompt: str = Form(""),
    num_inference_steps: int = Form(20),
    guidance_scale: float = Form(7.5),
    width: int = Form(1024),  # SDXL 기본 해상도
    height: int = Form(1024),  # SDXL 기본 해상도
    fast_mode: bool = Form(False)
):
    try:
        # 모델 초기화
        initialize_model(style)
        
        # 스타일별 프롬프트 수정
        if style == LoRAStyle.SURREAL:
            prompt = f"{prompt}, surreal landscape, dreamlike, ethereal, mystical, fantasy"
        
        # LCM 모드나 빠른 생성 모드일 때 스텝 수 조정
        if style == LoRAStyle.LCM:
            num_inference_steps = min(8, num_inference_steps)  # LCM은 4-8 스텝이 적당
            guidance_scale = 2.0  # LCM은 낮은 guidance scale이 좋음
        elif fast_mode:
            num_inference_steps = max(1, num_inference_steps // 2)
            
        # 이미지 생성
        with torch.no_grad():
            output = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                target_size=(width, height)
            )
        
        # 결과 이미지 처리
        image = output.images[0]
        
        # 이미지를 파일로 저장
        image_filename = f"{uuid.uuid4()}.png"
        image_path = IMAGES_DIR / image_filename
        image.save(image_path)
        
        # 오래된 이미지 정리
        cleanup_old_images()
        
        # base64 인코딩
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # 사용된 LoRA 정보
        used_loras = ["HelloworldXL"]
        if style != LoRAStyle.NONE:
            used_loras.append(str(style))
        
        return {
            "image": img_str,
            "file_path": f"/images/{image_filename}",
            "settings": {
                "style": style,
                "model": current_model_type,
                "loras": used_loras,
                "steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "scheduler": current_scheduler,
                "size": f"{width}x{height}"
            }
        }
        
    except Exception as e:
        print(f"이미지 생성 중 오류 발생: {e}")
        raise

@app.get("/images/{image_name}")
async def get_image(image_name: str):
    image_path = IMAGES_DIR / image_name
    if not image_path.exists():
        return {"error": "이미지를 찾을 수 없습니다."}
    return FileResponse(image_path)

@app.get("/styles")
async def get_styles():
    return {"styles": [style.value for style in LoRAStyle]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)