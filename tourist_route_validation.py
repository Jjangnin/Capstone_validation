import requests
import numpy as np
import itertools
from geopy.distance import geodesic

# 구글 API 키 (비공개 키 사용 금지)
API_KEY = 'AIzaSyCRK2h8-8IARsJzERnHe7Pp22HItbYVGE8'

# 삿포로 관광지 검색 (Google Places API)
def get_places_in_sapporo():
    places = {}
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query=tourist+attractions+in+sapporo&key={API_KEY}'

    # 페이지 처리를 위한 루프
    while url:
        response = requests.get(url)
        results = response.json().get('results', [])
        
        for place in results:
            name = place['name']
            lat = place['geometry']['location']['lat']
            lng = place['geometry']['location']['lng']
            places[name] = (lat, lng)
        
        # 다음 페이지로 이동
        url = response.json().get('next_page_token')
        if url:
            url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={url}&key={API_KEY}'

    return places

# 관광지 간의 거리 계산
def calculate_distance(loc1, loc2):
    return geodesic(loc1, loc2).kilometers

# 거리 행렬 만들기
def create_distance_matrix(locations):
    spots = list(locations.keys())
    distance_matrix = np.zeros((len(spots), len(spots)))
    
    for i, spot1 in enumerate(spots):
        for j, spot2 in enumerate(spots):
            if i != j:
                distance_matrix[i][j] = calculate_distance(locations[spot1], locations[spot2])
    
    return distance_matrix, spots

# 외판원 문제 해결: 최단 경로
def tsp(distance_matrix):
    num_spots = len(distance_matrix)
    
    if num_spots == 1:
        return [0], 0  # 관광지가 하나일 경우, 자기 자신만 돌아보면 됨
    
    all_routes = itertools.permutations(range(num_spots))
    min_route = None
    min_distance = float('inf')
    
    for route in all_routes:
        route_distance = 0
        for i in range(len(route) - 1):
            route_distance += distance_matrix[route[i]][route[i + 1]]
        route_distance += distance_matrix[route[-1]][route[0]]  # 마지막 도시에서 첫 도시로 돌아오는 거리
        
        if route_distance < min_distance:
            min_distance = route_distance
            min_route = route
    
    return min_route, min_distance

# 삿포로의 관광지 정보를 가져오고 최단 경로 계산
places_in_sapporo = get_places_in_sapporo()

# 관광지 정보가 10개 이상이면, 너무 많은 계산을 피하기 위해 샘플로 일부만 선택
if len(places_in_sapporo) > 10:
    places_in_sapporo = dict(itertools.islice(places_in_sapporo.items(), 10))

distance_matrix, spots = create_distance_matrix(places_in_sapporo)
min_route, min_distance = tsp(distance_matrix)

# 최단 경로 출력
print("📌 최단 관광지 방문 경로:")
for i in min_route:
    print(spots[i])

print(f"📊 최단 거리: {min_distance:.2f} km")

