## 📝 프로젝트 소개
기존의 텍스트 기반 입력 방식에서 벗어나 이미지 인식 기술을 활용해 식단 기록의 편리성을 높이고, 사용자의 건강 관리에 실질적인 도움을 제공하는 것을 목표로 합니다.

## 🔧 Stack
### Frontend

- Language : HTML, Python
- Framework : Streamlit

### Backend

- Language : Python
- Library & Framework : FastAPI
  
### Infrastructure
- Cloud Platform : AWS(EC2)
- OS: Linux(Ubuntu)

### Deployment
- Github Actions
- Docker
- Kubernetes


## ⚙️ 개발/배포 아키텍처
![Image](https://github.com/user-attachments/assets/4e8444a9-e0a1-47ea-b811-019714adcd63)

### 배포 프로세스
main 브랜치에 코드를 푸시하면 GitHub Actions가 트리거되어 자동으로 배포 파이프라인이 실행됩니다.

#### 이미지 빌드&푸시
각각의 서비스(프론트엔드 Streamlit, 백엔드 FastAPI)에 대해 Docker 이미지를 빌드합니다.
빌드된 이미지를 Docker Hub에 푸시하여 중앙 저장소에 보관합니다.

#### AWS EC2 서버 접속 및 배포
docker-compose를 사용해 최신 이미지를 내려받고
최신 이미지로 컨테이너를 재생성 및 실행

