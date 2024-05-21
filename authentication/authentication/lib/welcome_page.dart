import 'package:flutter/material.dart';

class WelcomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome Page'),
      ),
      body: Center(
        child: Text(
          'payment is successful!',
          style: TextStyle(fontSize: 24),
        ),
      ),
    );
  }
}
