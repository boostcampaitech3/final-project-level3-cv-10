![header](https://capsule-render.vercel.app/api?type=waving&color=0:bee1e8,100:ddc7fc&height=250&section=header&text=인물%20기반%20예능%20숏폼%20영상%20생성기%2c%20%23눈%23사람&fontColor=262626&desc=예능%20영상에서%20원하는%20인물의%20하이라이트%20쇼츠를%20간편하게%20생성할%20수%20있습니다.&fontAlignY=35&descAlignY=52&fontSize=40&descSize=20&animation=fadeIn)

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=black"> <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=Jupyter&logoColor=white">    
<img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=PyTorch&logoColor=white"> <img src="https://img.shields.io/badge/Dlib-008000?style=for-the-badge&logo=Dlib&logoColor=white"> <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=OpenCV&logoColor=white"> <img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=FFmpeg&logoColor=white">  
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white"> <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black">  

<br>

## Service URL
TBA

<br>

## Members
> 안녕하세요, CV-10 #눈#사람 팀입니다.

| 김하준 | 송민수 | 심준교 | 유승리 | 이창진 | 전영우 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| ![눈사람_김하준](https://user-images.githubusercontent.com/43572543/164686306-5f2618e9-90b0-4446-a193-1c8e7f1d77ad.png) | ![눈사람_송민수](https://user-images.githubusercontent.com/43572543/164686145-4030fd4f-bdd1-4dfa-9495-16d7c7689731.png) | ![눈사람_심준교](https://user-images.githubusercontent.com/43572543/164686612-d221b3c9-8895-4ac4-af4e-385412afe541.png) | ![눈사람_유승리](https://user-images.githubusercontent.com/43572543/164686476-0b3374d4-1f00-419c-ae5a-ecd37227c1ef.png) | ![눈사람_이창진](https://user-images.githubusercontent.com/43572543/164686491-c7acc30f-7175-4ce5-b2ea-46059857d955.png) | ![눈사람_전영우](https://user-images.githubusercontent.com/43572543/164686498-d251b498-b3fa-4c3c-b5f9-7cd2b62ed58b.png) |
|`Modeling`|`Serving`|`Modeling`|`Serving`|`Modeling`|`Modeling`|
|[GitHub](https://github.com/HajunKim)|[GitHub](https://github.com/sooya233)|[GitHub](https://github.com/Shimjoonkyo)|[GitHub](https://github.com/seungriyou)|[GitHub](https://github.com/noisrucer)|[GitHub](https://github.com/wowo0709)|

<br>

## Introduction
### Background
- 예능 프로그램은 게스트를 중심으로 편집되어 여러 플랫폼에 하이라이트 편집본으로 올라오지만, 전문 인력이 직접 수행해야하는 편집 과정은 **큰 시간과 비용을 요구**합니다. 
- 최근 영상 소비의 트렌드는 가볍게 즐길 수 있는 **1분 내외 길이인 '숏폼' 영상**으로, 동일 영상 대비 숏폼으로 편집될 경우 더 많은 조회수와 더 다양한 플랫폼에서 노출의 기회를 얻습니다. 

### Contribution
- 기존 전문 인력이 직접 수행하던 편집과정을 **자동화**하여 **시간과 비용을 최소화**합니다.
- 게스트 중심으로 영상을 보고싶은 **사용자들의 니즈**를 충족시키는 **인물 기반 편집 방법론**을 제시합니다.
- **예능의 특성**과 **숏폼의 특징**을 모두 고려한 편집 방법론을 제시합니다.

<br>

<img width="1458" alt="전체_flow" src="https://user-images.githubusercontent.com/43572543/173187784-3291c4ea-d833-43a7-a333-d3285a3a0ec2.png">

<br>

## System Flow
### [1] 영상 업로드 시 Person Clustering 및 Laughter Detection 수행

<img src="https://user-images.githubusercontent.com/43572543/173084985-387484db-51f2-46a3-a1c4-f3c4d9b3b078.gif" width="600" />

#### Scene Detection & Person Clustering
- **화면이 전환**되는 장면을 detect 한 후, 해당 장면들에서 인물의 **face**와 **clothing** 정보를 이용하여 **영상에 등장하는 인물을 파악**합니다.
- **face landmark**와 **clothing**에 대한 feature vector를 normalize 후 concat하여 **HAC**(Hierarchical Agglomerative Clustering)을 수행합니다.
- 여러 후처리를 통해 clustering 성능을 더욱 향상시키고, 각 인물 cluster 별로 **가장 선명한 사진**을 선택하여 사용자에게 제시합니다.

#### Laughter Detection
- 예능 영상의 음성 파일에서 **laughter timeline**(웃음이 등장하는 타임라인)을 추출합니다.
- 웃음 구간이 짧은 타임라인은 병합한 후, 맥락을 포함하기 위해 각 타임라인에 **[-15초, +0.5초]** 를 추가하여 숏폼 영상 후보군을 생성합니다.
- laughter detection을 수행하는 서버는 따로 두어 다른 동작과 **병렬적으로 동시에 수행**됩니다.

<br>

### [2] 인물 선택 시 Person Recognition 수행 후 숏폼 영상 생성

<img src="https://user-images.githubusercontent.com/43572543/173085027-cf4954da-8bc7-4b9f-92c9-afeb41634e7c.gif" width="600" />

#### Person Recognition
- person clustering과 동일하게 사용자가 선택한 인물의 **face**와 **clothing** 정보를 이용하여 **person timeline**(인물이 등장하는 타임라인)을 추출합니다.
- 이때, feature vector로는 앞서 clustering에서 구한 vector 값들의 평균 값을 사용합니다.

#### Final Timeline & Interest Estimation
- **laughter timeline**과 **person timeline**을 결합하여 **final timeline**(타겟 인물이 일정 비율 이상으로 등장하는 최종 숏폼 영상 후보군)을 계산하고 숏폼 영상을 생성합니다.
- 각 final timeline에 대해 다음의 세 가지 feature의 weighted sum을 통해 **흥미도를 계산**합니다.
  ```
  (1) 영상 내 평균 웃음 소리 길이
  (2) 영상 내 평균 웃음 소리 크기
  (3) 해당 인물의 등장 비율
  ```

<br>

### [3] 생성된 숏폼 영상 확인 및 다운로드
> 생성된 숏폼 영상은 흥미도 순으로 정렬됩니다.

<img src="https://user-images.githubusercontent.com/43572543/173085034-3700f373-707e-411c-a89c-bec6abea7c1f.gif" width="600" />

<br>

## System Architecture
<img width="1460" alt="시스템_구성도" src="https://user-images.githubusercontent.com/43572543/173222768-49aad704-4730-4992-ab77-ce183cc90085.png">

<br>

## How to Run
### Modeling
TBA

### Serving
TBA

<br>

## Reference
### Papers
- Gillick, Jon, et al. "Robust Laughter Detection in Noisy Environments." Proc. Interspeech 2021 (2021): 2481-2485. [[PAPER]](https://www.isca-speech.org/archive/pdfs/interspeech_2021/gillick21_interspeech.pdf) [[CODE]](https://github.com/jrgillick/laughter-detection)
- Brown, Andrew, Vicky Kalogeiton, and Andrew Zisserman. "Face, body, voice: Video person-clustering with multiple modalities." Proceedings of the IEEE/CVF International Conference on Computer Vision. 2021. [[PAPER]](https://arxiv.org/pdf/2105.09939.pdf)


### Open Source
- Face Recognition [[CODE]](https://github.com/ageitgey/face_recognition)

<br>

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:bee1e8,100:ddc7fc&height=200&section=footer)
