# Git & GitHub Flow Branch 전략

## 1. Git Flow란?

Git Flow는 `main`, `develop`, `feature`, `release`, `hotfix` 등 여러 종류의 브랜치를 목적에 따라 세분화하여 관리하는 전략이다.

- **main**: 실제 배포되는 안정 버전만 존재하는 브랜치
- **develop**: 다음 배포를 위한 개발 내용이 통합되는 브랜치
- **feature/\***: 개별 기능을 개발하는 브랜치 (develop에서 분기, develop으로 병합)
- **release/\***: 배포 전 최종 점검을 위한 브랜치
- **hotfix/\***: 배포 후 발생한 긴급 버그를 수정하는 브랜치 (main에서 분기, main과 develop에 병합)

브랜치 종류가 많아 관리가 체계적이지만, 그만큼 절차가 복잡해서 배포 주기가 길고 버전 관리가 엄격한 대규모 프로젝트에 적합하다.

## 2. GitHub Flow란?

GitHub Flow는 `main` 브랜치 하나와 기능별 `feature` 브랜치만으로 운영하는 단순한 전략이다.

작업 흐름은 다음과 같다.

1. `main`에서 새로운 `feature` 브랜치를 분기한다.
2. 해당 브랜치에서 기능을 개발하고 커밋한다.
3. 원격 저장소로 push한다.
4. Pull Request(PR)를 생성한다.
5. 팀원의 코드 리뷰를 받는다.
6. 리뷰 승인 후 `main`으로 merge한다.

브랜치 구조가 단순해서 배포 주기가 짧고 빠른 반복 개발이 필요한 프로젝트에 적합하다.

## 3. Git Flow vs GitHub Flow 비교

| 구분 | Git Flow | GitHub Flow |
|---|---|---|
| 브랜치 종류 | main, develop, feature, release, hotfix | main, feature |
| 복잡도 | 높음 | 낮음 |
| 배포 주기 | 김 (버전 단위 배포) | 짧음 (수시 배포) |
| 적합한 프로젝트 | 대규모, 정기 배포가 필요한 프로젝트 | 소규모, 빠른 반복 개발이 필요한 프로젝트 |

## 4. 우리 팀의 선택: GitHub Flow

우리 팀은 **GitHub Flow**를 채택한다.

**선택 이유**

- 과제 진행 기간이 7/13 ~ 7/29로 약 2주 정도의 단기 프로젝트라 복잡한 버전 관리가 필요하지 않다.
- 팀 규모가 5명으로 크지 않아 브랜치를 세분화할 필요성이 적다.
- 기능 단위로 빠르게 개발하고 바로 리뷰 후 병합하는 방식이 학습 목적에 더 적합하다.

**적용 방식**

1. `main`에서 `feature/기능명` 브랜치를 생성한다. (예: `feature/user-api`)
2. 해당 브랜치에서 기능을 개발하고 커밋한다. (커밋 메시지는 팀 규칙의 컨벤션을 따른다)
3. 원격 저장소로 push한다.
4. `main`을 대상으로 Pull Request를 생성한다.
5. 팀원 1명 이상의 리뷰 승인을 받는다.
6. 승인 후 `main`에 merge하고, 작업이 끝난 feature 브랜치는 삭제한다.

## 참고자료

- https://velog.io/@myoungji-kim/git-flow
- https://devocean.sk.com/blog/techBoardDetail.do?ID=165571&boardType=techBlog
- https://www.heropy.dev/p/6hdJi6
