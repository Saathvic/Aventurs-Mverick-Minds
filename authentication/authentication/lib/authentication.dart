import 'package:flutter/material.dart';
import 'package:vibration/vibration.dart';
import 'welcome_page.dart';

class AuthenticationPage extends StatefulWidget {
  @override
  _AuthenticationPageState createState() => _AuthenticationPageState();
}

class _AuthenticationPageState extends State<AuthenticationPage> {
  List<int> _pattern = [];
  List<List<int>> _grid = [
    [1, 2],
    [3, 4],
    [5, 6],
  ];

  void _onButtonPressed(int number) async {
    _pattern.add(number);

    // Provide haptic feedback for button press
    await Vibration.vibrate(duration: 100);

    // Check pattern (example pattern: [1, 2, 3, 4])
    if (_pattern.length == 4) {
      if (_pattern.equals([1, 2, 3, 4])) {
        // Navigate to next page (WelcomePage)
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => WelcomePage()),
        );

        // Provide haptic feedback for correct pattern
        await Vibration.vibrate(
            duration:
                2200); // Duration changed to 2.2 seconds for correct pattern

        _pattern.clear();
      } else {
        // Provide haptic feedback for incorrect pattern
        await Vibration.vibrate(
            duration:
                7000); // Duration changed to 7 seconds for incorrect pattern

        _pattern.clear();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Calculate the size of each grid item based on screen size
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    final itemWidth = screenWidth / 2; // Divide screen width into 2 parts
    final itemHeight = screenHeight / 3; // Divide screen height into 3 parts

    return Scaffold(
      backgroundColor: Colors.black, // Black background
      body: Center(
        child: GestureDetector(
          onTapDown: (details) {
            // Calculate the region based on tap position
            final double width = itemWidth;
            final double height = itemHeight;
            final int region = (details.localPosition.dx ~/ width) +
                ((details.localPosition.dy ~/ height) * 2) +
                1;

            // Validate region and add to pattern
            if (region >= 1 && region <= 6) {
              _onButtonPressed(region);
            }
          },
          child: GridView.count(
            crossAxisCount: 2, // Divide into 2 columns
            childAspectRatio:
                itemWidth / itemHeight, // Aspect ratio to fill the screen
            children: List.generate(6, (index) {
              final number = _grid[index ~/ 2][index % 2];
              return Container(
                color: Colors.transparent,
                child: Center(
                  child: Text(
                    '$number',
                    style: TextStyle(
                        fontSize: 24,
                        color: Colors.black), // Set text color to black
                  ),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}

extension ListEquality<T> on List<T> {
  bool equals(List<T> other) {
    if (this.length != other.length) return false;
    for (int i = 0; i < this.length; i++) {
      if (this[i] != other[i]) return false;
    }
    return true;
  }
}
