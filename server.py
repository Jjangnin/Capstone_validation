from flask import Flask, request, jsonify
import googlemaps
from flask_cors import CORS

app = Flask(__name__)

# CORS 설정을 명확히: 모든 origin 허용 (개발용)
CORS(app, resources={r"/recommend": {"origins": "*"}})

# 실제 배포시에는 환경변수로 API 키를 보관하세요
API_KEY = 'AIzaSyCRK2h8-8IARsJzERnHe7Pp22HItbYVGE8'
gmaps = googlemaps.Client(key=API_KEY)

@app.route('/recommend', methods=['POST'])
def recommend_places():
    data = request.get_json()
    user_keywords = data.get('keywords', [])

    if not user_keywords:
        return jsonify({'error': 'No keyword provided'}), 400

    keyword = user_keywords[0]
    final_recommendations = []

    try:
        print(f"🔍 [Step 1] 검색 키워드: {keyword}")
        origin_result = gmaps.places(query=f'{keyword} in South Korea')
        origin_places = origin_result.get('results', [])

        if not origin_places:
            print("⚠️ 한국에서 해당 키워드 결과 없음")
            return jsonify({'recommendations': []})

        origin_place = origin_places[0]
        origin_types = origin_place.get('types', [])

        print(f"🏷️ 원본 장소 유형(types): {origin_types}")

        # Step 2: 일본에서 유사 장소 검색
        if origin_types:
            filtered_types = [t for t in origin_types if t not in ['point_of_interest', 'establishment']]
            type_query = ' '.join(filtered_types[:2]) if filtered_types else keyword
        else:
            type_query = keyword

        search_query = f"{type_query} in Japan"
        print(f"🌏 [Step 2] 일본 유사 장소 검색 쿼리: {search_query}")
        similar_places_result = gmaps.places(query=search_query, region='jp')
        similar_places = similar_places_result.get('results', [])

        # Step 3: 최대 5개 장소 반환
        for place in similar_places[:5]:
            address = place.get('formatted_address') or place.get('vicinity') or 'No address'
            final_recommendations.append({
                'name': place.get('name'),
                'rating': place.get('rating', 'No rating'),
                'address': address,
                'types': place.get('types', []),
            })

        print(f"✅ [완료] 추천 장소 개수: {len(final_recommendations)}")
        return jsonify({'recommendations': final_recommendations})

    except Exception as e:
        print(f"❌ [에러] {str(e)}")
        return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

# 웹 접근 허용을 위해 host='0.0.0.0'으로 변경
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
