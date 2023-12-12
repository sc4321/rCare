package com.remotecare.watchover_1;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.FirebaseApp;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
//import com.google.firebase.FirebaseLogger;

import com.squareup.picasso.Picasso;

import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import static androidx.fragment.app.FragmentManager.TAG;

public class MainActivity extends AppCompatActivity implements myFirebaseDatabase.ImageListenerCallback {
    ImageView alarmImg;
    TextView imgName;
    private myFirebaseDatabase db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        alarmImg = (ImageView) findViewById(R.id.alarmImage);
        imgName = (TextView) findViewById(R.id.imageNameTextView);

        db = myFirebaseDatabase.getInstance();
        db.setCallback(this);

        // db.logOut();

        if (!db.isUserLoggedIn()) {
            sendUserToLoginActivity();
            return;  // Return to avoid further execution of code
        }
        else {
            Toast.makeText(getApplicationContext(), "logged in with email" + db.getUserEmail(), Toast.LENGTH_LONG);
        }
        imgName.setText("after the initialization");


         /*

        // Initialize Firebase
        FirebaseApp.initializeApp(this);

        // Initialize Firebase Authentication
        FirebaseAuth auth = FirebaseAuth.getInstance();
        auth.signInWithEmailAndPassword("binyaminc6@gmail.com", "123456")
                .addOnCompleteListener(new OnCompleteListener<AuthResult>() {
            @Override
            public void onComplete(@NonNull Task<AuthResult> task) {

                FirebaseDatabase database = FirebaseDatabase.getInstance();
                DatabaseReference myRef = database.getReference("/cameras/96a7ba21-7922-5ed0-aca3-029df2a54cc2/image_data");

                // Read from the database
                myRef.addValueEventListener(new ValueEventListener() {
                    @Override
                    public void onDataChange(DataSnapshot dataSnapshot) {
                        // This method is called once with the initial value and again
                        // whenever data at this location is updated.
                        String imgURL = dataSnapshot.getValue(String.class);
                        Log.d("Main", "IMG URL:   " + imgURL);

                        Picasso.get().load(imgURL).into(alarmImg);
                        imgName.setText(imgURL);
                    }

                    @Override
                    public void onCancelled(DatabaseError error) {
                        // Failed to read value
                        Log.w("Main", "Failed to read value.", error.toException());
                    }
                });

            }
        });

        // Enable Firebase logging
        //FirebaseLogger.getInstance().setLogLevel(Log.DEBUG);

        String email = "your_email@example.com";
        String password = "your_password";


        FirebaseDatabase database = FirebaseDatabase.getInstance();
        DatabaseReference myRef = database.getReference("message");
        myRef.setValue("Hello, World on create!");

        myRef = database.getReference("/cameras/96a7ba21-7922-5ed0-aca3-029df2a54cc2/image_data");

        // Read from the database
        myRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                // This method is called once with the initial value and again
                // whenever data at this location is updated.
                String imgURL = dataSnapshot.getValue(String.class);
                Log.d("Main", "IMG URL:   " + imgURL);

                Picasso.get().load(imgURL).into(alarmImg);
                imgName.setText(imgURL);
            }

            @Override
            public void onCancelled(DatabaseError error) {
                // Failed to read value
                Log.w("Main", "Failed to read value.", error.toException());
            }
        });
        */

    }

    private void sendUserToLoginActivity() {
        Intent loginIntent = new Intent(getApplicationContext(), LoginActivity.class);
        startActivity(loginIntent);
        finish(); // Finish the MainActivity to prevent it from being on the back stack
    }

    @Override
    public void onImageChange(Bitmap bitmap, String imgURL, Long timestamp) {

        if (bitmap != null) {
            alarmImg.setImageBitmap(bitmap);
        }
        else {
            Toast.makeText(getApplicationContext(), "bitmap is null", Toast.LENGTH_LONG);
        }
        imgName.setText(imgURL);
    }
}