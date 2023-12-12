package com.remotecare.watchover_1;

import android.graphics.Bitmap;
import android.graphics.drawable.Drawable;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.squareup.picasso.Picasso;
import com.squareup.picasso.Target;

import androidx.annotation.NonNull;

public class myFirebaseDatabase {

    private static myFirebaseDatabase ourInstance = null;

    private FirebaseDatabase database;
    private DatabaseReference camRef;
    private FirebaseAuth mAuth;
    private FirebaseUser currentUser;

    public interface ImageListenerCallback {
        void onImageChange(Bitmap bitmap, String imgURL, Long timestamp);
    }
    private ImageListenerCallback callback;

    // function to implement singleton
    public static myFirebaseDatabase getInstance() {
        if (ourInstance == null)
            ourInstance = new myFirebaseDatabase();
        return ourInstance;
    }

    private myFirebaseDatabase(){
        database = FirebaseDatabase.getInstance();  // (databaseURL)
        mAuth = FirebaseAuth.getInstance();
    }

    public boolean isUserLoggedIn() {
        FirebaseUser user = mAuth.getCurrentUser();
        return user != null;
    }

    public String getUserEmail() {
        String mail = mAuth.getCurrentUser().getEmail();
        return mail;
    }

    public void setCallback(ImageListenerCallback callback) {
        this.callback = callback;
    }

    void login(String email, String password, final LoginActivity loginActivity){  // final LoginActivity activity){
        mAuth.signInWithEmailAndPassword(email, password)
                .addOnCompleteListener(new OnCompleteListener<AuthResult>() {
                    @Override
                    public void onComplete(Task<AuthResult> task) {
                        if(task.isSuccessful()) {
                            currentUser = mAuth.getCurrentUser();
                            camRef = database.getReference("/cameras/96a7ba21-7922-5ed0-aca3-029df2a54cc2");

//                            DatabaseReference myRef = database.getReference("/cameras/96a7ba21-7922-5ed0-aca3-029df2a54cc2/image_data_2");
//                            myRef.setValue("Hello, World on create!");

                            camRef.addValueEventListener(new ValueEventListener() {
                                @Override
                                public void onDataChange(@NonNull DataSnapshot snapshot) {
                                    String imgURL = snapshot.child("/image_data").getValue(String.class);
                                    Long timestamp = snapshot.child("/timestamp").getValue(Long.class);

                                    Picasso.get().load(imgURL).into(new Target() {
                                                @Override
                                                public void onBitmapLoaded(Bitmap bitmap, Picasso.LoadedFrom from) {
                                                    if (callback != null) {
                                                        callback.onImageChange(bitmap, imgURL, timestamp);
                                                    }
                                                }
                                                @Override
                                                public void onBitmapFailed(Exception e, Drawable errorDrawable) {
                                                    int x = 0;
                                                }
                                                @Override
                                                public void onPrepareLoad(Drawable placeHolderDrawable) {
                                                    int x = 0;
                                                }
                                            });
                                    loginActivity.afterSuccessfulLogin();
                                }

                                @Override
                                public void onCancelled(@NonNull DatabaseError error) {
                                    loginActivity.afterFailedLogin("couldn't add listener to URL");
                                }
                            });
                        }
                        else {
                            String message = task.getException().toString();
                            loginActivity.afterFailedLogin(message);
                        }
                    }
                });
    }

    void logOut() {
        mAuth.signOut();
    }
}
