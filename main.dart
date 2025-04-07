import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '관광지 추천',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: RecommendScreen(),
    );
  }
}

class RecommendScreen extends StatefulWidget {
  @override
  _RecommendScreenState createState() => _RecommendScreenState();
}

class _RecommendScreenState extends State<RecommendScreen> {
  final TextEditingController _controller = TextEditingController();
  List<dynamic> recommendations = [];
  bool isLoading = false;

  Future<void> fetchRecommendations(String keyword) async {
    setState(() {
      isLoading = true;
      recommendations = [];
    });

    try {
      // 🌐 Flutter Web에서는 localhost 사용
      final response = await http.post(
        Uri.parse('http://localhost:5000/recommend'),  // 수정된 부분
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'keywords': [keyword]}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          recommendations = data['recommendations'];
        });
      } else {
        print('서버 오류: ${response.statusCode}');
      }
    } catch (e) {
      print('에러 발생: $e');
    }

    setState(() {
      isLoading = false;
    });
  }

  Widget buildRecommendationList() {
    if (recommendations.isEmpty) {
      return Center(child: Text('추천 결과가 없습니다.'));
    }

    return ListView.builder(
      itemCount: recommendations.length,
      itemBuilder: (context, index) {
        final place = recommendations[index];
        return Card(
          margin: EdgeInsets.symmetric(vertical: 8),
          child: ListTile(
            title: Text(place['name'] ?? '이름 없음'),
            subtitle: Text(
              '주소: ${place['address'] ?? '주소 없음'}\n'
                  '평점: ${place['rating'] ?? 'N/A'}\n'
                  '종류: ${(place['types'] as List<dynamic>?)?.join(', ') ?? '없음'}',
            ),
            isThreeLine: true,
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('관광지 추천')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                labelText: '검색',
                suffixIcon: IconButton(
                  icon: Icon(Icons.search),
                  onPressed: () {
                    final keyword = _controller.text.trim();
                    if (keyword.isNotEmpty) {
                      fetchRecommendations(keyword);
                    }
                  },
                ),
              ),
            ),
            SizedBox(height: 20),
            Expanded(
              child: isLoading
                  ? Center(child: CircularProgressIndicator())
                  : buildRecommendationList(),
            ),
          ],
        ),
      ),
    );
  }
}
