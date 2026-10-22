# 공개 링크 점검 방법

웹사이트 등록 신청이나 서비스 대시보드의 숫자는 실제 공개 링크와 다를 수 있습니다. 이 도구는 출처 페이지를 다시 열어 지정한 주소로 연결되는 HTML 링크를 찾고, HTTP 응답과 검색 제외 표시를 함께 기록합니다.

## 확인 순서

1. 출처 웹 주소를 한 줄에 하나씩 텍스트 파일에 적습니다.
2. 점검할 대상 주소를 `--target`으로 지정합니다.
3. 결과 CSV에서 `exact_href`, `http_status`, `noindex`, `link_rel`을 확인합니다.
4. 시간이 지난 뒤 같은 목록을 다시 확인하여 링크가 유지되는지 살펴봅니다.

```bash
python3 verify_links.py --target https://vietnabi.com/ --sources sources.txt --output results.csv
```

베트남 여행 정보 사이트 [베트나비](https://vietnabi.com/)의 링크도 같은 기준으로 확인합니다. 링크가 페이지에 보인다는 사실과 검색엔진의 색인 여부는 서로 다른 결과입니다. 자바스크립트 실행 후 생성되는 링크는 이 도구의 HTML 검사만으로 확인할 수 없으므로 별도 브라우저 검사가 필요합니다.

[소스 코드와 사용 설명](https://github.com/daimai3/public-link-verifier)
