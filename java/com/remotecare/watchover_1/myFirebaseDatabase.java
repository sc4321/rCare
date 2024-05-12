package com.remotecare.watchover_1;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;

import androidx.annotation.NonNull;

public class myFirebaseDatabase {

    private static myFirebaseDatabase ourInstance = null;

    private FirebaseDatabase database;
    private DatabaseReference camRef;
    private FirebaseAuth mAuth;
    private FirebaseStorage firebaseStorage;
    private StorageReference storageReference;


    public interface ImageListenerCallback {
        void onImageChange(Bitmap bitmap, String imgURL, Long timestamp);
        void onFailure(String message);
    }
    private ImageListenerCallback callback;

    // function to implement singleton
    public static myFirebaseDatabase getInstance() {
        if (ourInstance == null)
            ourInstance = new myFirebaseDatabase();
        return ourInstance;
    }

    private myFirebaseDatabase(){
        database = FirebaseDatabase.getInstance();
        mAuth = FirebaseAuth.getInstance();

        firebaseStorage = FirebaseStorage.getInstance();
        storageReference = firebaseStorage.getReference();
    }

    public boolean isUserLoggedIn() {
        FirebaseUser user = mAuth.getCurrentUser();
        return user != null;
    }

    public String getUserEmail() {
        String mail = mAuth.getCurrentUser().getEmail();
        return mail;
    }

    void login(String email, String password, final LoginActivity loginActivity){  // final LoginActivity activity){
        mAuth.signInWithEmailAndPassword(email, password)
                .addOnCompleteListener(task -> {
                    if(task.isSuccessful()) {
                        loginActivity.afterSuccessfulLogin();
                    }
                    else {
                        String message = task.getException().toString();
                        loginActivity.afterFailedLogin(message);
                    }
                });
    }

    public void setCallback(ImageListenerCallback callback) {
        this.callback = callback;
    }

    void setListenerToImages() {
        camRef = database.getReference("/cameras/96a7ba21-7922-5ed0-aca3-029df2a54cc2");

        camRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                String imgURL = snapshot.child("/image_data").getValue(String.class);
                String imgName = imgURL.substring(imgURL.lastIndexOf('/') + 1);

                Long timestamp = snapshot.child("/timestamp").getValue(Long.class);

                StorageReference imgRef = storageReference.child("/images/" + imgName);
                long MAXBYTES = 1024*1024;

                imgRef.getBytes(MAXBYTES).addOnCompleteListener(task -> {
                    if (task.isSuccessful()) {
                        byte[] bytes = task.getResult();
                        Bitmap bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.length);
                        callback.onImageChange(bitmap, imgURL, timestamp);
                    } else {
                        // Handle failure
                        String message = task.getException().toString();
                        callback.onFailure(message);
                    }
                });
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                callback.onFailure("couldn't add listener to the camera");
            }
        });
    }

    void logOut() {
        mAuth.signOut();
    }
}
