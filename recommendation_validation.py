import pandas as pd
import googlemaps

# 유저 클릭 데이터 불러오기
user_clicks = pd.read_csv(r'C:\Users\Administrator\OneDrive\바탕 화면\캡스톤\Capstone_test\user_clicks.csv')  # CSV 파일 경로 수정

# Google Maps API 키 설정
API_KEY = 'AIzaSyCRK2h8-8IARsJzERnHe7Pp22HItbYVGE8'  # 실제 구글 API 키로 대체하세요.
gmaps = googlemaps.Client(key=API_KEY)

# 유저 클릭 데이터에서 types 추출 (각 관광지의 types 정보)
def get_user_types(user_clicks):
    user_types = []
    for types in user_clicks['types']:
        user_types.extend(types.split('|'))  # 여러 types을 구분자로 나누어 리스트로 추가
    return set(user_types)  # 중복 제거하여 반환

# 유사한 관광지 추천
def get_similar_places_recommendations(user_types, num_recommendations=5):
    recommendations = []

    for place_type in user_types:
        # Google Places API로 해당 type의 관광지 검색
        places_result = gmaps.places(query=f'tourist attractions of type {place_type}', type=place_type)
        
        # 결과에서 관광지 정보를 추천 리스트에 추가
        for place in places_result['results'][:num_recommendations]:
            recommendations.append({
                'type': place_type,
                'name': place['name'],
                'rating': place.get('rating', 'No rating'),
                'address': place.get('formatted_address', 'Address not available'),
                'types': place.get('types', [])
            })
    
    return recommendations

# 유저 클릭 데이터에서 types 추출
user_types = get_user_types(user_clicks)

# 추천 관광지 가져오기
recommended_places = get_similar_places_recommendations(user_types)

# 추천 결과 출력
print("추천된 관광지:")
for place in recommended_places:
    print(f"유형: {place['type']}, 관광지명: {place['name']}, 평점: {place['rating']}, 주소: {place['address']}, 유형: {', '.join(place['types'])}")

# 추천 정확도를 평가하기 위한 검증 코드

def evaluate_recommendations(recommended_places, user_types):
    matched_count = 0  # 일치하는 추천 관광지 수
    total_recommendations = len(recommended_places)  # 추천된 관광지 수

    for place in recommended_places:
        # 추천된 관광지의 types가 유저가 클릭한 types 중 하나와 일치하는지 확인
        for place_type in place['types']:
            if place_type in user_types:
                matched_count += 1
                break  # 하나라도 일치하면 일치로 간주

    # 정확도 계산 (추천된 관광지 중 일치하는 비율)
    accuracy = matched_count / total_recommendations if total_recommendations > 0 else 0
    return accuracy, matched_count, total_recommendations

# 추천 정확도 계산
accuracy, matched_count, total_recommendations = evaluate_recommendations(recommended_places, user_types)

# 평가 결과 출력
print("\n추천 정확도 평가:")
print(f"추천된 관광지 수: {total_recommendations}")
print(f"일치하는 관광지 수: {matched_count}")
print(f"추천 정확도: {accuracy * 100:.2f}%")
