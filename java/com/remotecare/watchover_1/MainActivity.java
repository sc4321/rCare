package com.remotecare.watchover_1;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;


public class MainActivity extends AppCompatActivity implements myFirebaseDatabase.ImageListenerCallback {
    ImageView alarmImg;
    TextView imgName, imgTime;
    private myFirebaseDatabase db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        alarmImg = findViewById(R.id.alarmImage);
        imgName = findViewById(R.id.imageNameTextView);
        imgName.setText("No images yet");
        imgTime = findViewById(R.id.imageTimeTextView);

        db = myFirebaseDatabase.getInstance();

        if (!db.isUserLoggedIn()) {
            sendUserToLoginActivity();
            return;  // Return to avoid further execution of code
        }
        else {
            db.setCallback(this);
            db.setListenerToImages();
        }
    }

    private void sendUserToLoginActivity() {
        Intent loginIntent = new Intent(getApplicationContext(), LoginActivity.class);
        startActivity(loginIntent);
        finish(); // Finish the MainActivity to prevent it from staying on the activity stack
    }

    @Override
    public void onImageChange(Bitmap bitmap, String imgURL, Long timestamp) {

        if (bitmap != null) {
            alarmImg.setImageBitmap(bitmap);
        }
        else {
            Toast.makeText(getApplicationContext(), "image bitmap is null", Toast.LENGTH_LONG).show();
        }
        imgName.setText(imgURL);
        String time = "" + timestamp; // TODO: convert timestamp to some readable string
        imgTime.setText(time);
    }

    @Override
    public void onFailure(String message) {
        Toast.makeText(getApplicationContext(), message, Toast.LENGTH_LONG).show();
    }
}