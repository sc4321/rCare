package com.remotecare.watchover_1;

import androidx.appcompat.app.AppCompatActivity;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

public class LoginActivity extends AppCompatActivity {

    private EditText emailEditText, passwordEditText;
    private Button loginButton;

    public ProgressDialog loadingBar;

    LoginActivity loginActivity = this;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        initializeFields();

        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                String email = emailEditText.getText().toString();
                String password = passwordEditText.getText().toString();
                if(email.isEmpty()) {
                    Toast.makeText(getApplicationContext(), "email is empty", Toast.LENGTH_LONG).show();
                    return;
                }
                if(password.isEmpty()) {
                    Toast.makeText(getApplicationContext(), "password is empty", Toast.LENGTH_LONG).show();
                    return;
                }
                // create loading bar
                loadingBar.setTitle("Log In");
                loadingBar.setMessage("Please wait, while we log in to your account...");
                loadingBar.setCanceledOnTouchOutside(true);
                loadingBar.show();

                // login to the database
                (myFirebaseDatabase.getInstance()).login(email, password, loginActivity);
            }
        });
    }

    private void initializeFields() {

        emailEditText = findViewById(R.id.gmailEditText);
        passwordEditText = findViewById(R.id.passwordEditText);
        loginButton = findViewById(R.id.loginButton);

        loadingBar = new ProgressDialog(this);
    }

    public void sendUserToMainActivity() {
        Intent mainIntent = new Intent(getApplicationContext(), MainActivity.class);
        startActivity(mainIntent);
        finish();
    }

    public void afterSuccessfulLogin() { //this function is called from myFirebaseDatabase.login
        loadingBar.dismiss();
        sendUserToMainActivity();
    }
    public void afterFailedLogin(String errorMessage) { //this function is called from myFirebaseDatabase.login
        loadingBar.dismiss();
        Toast.makeText(getApplicationContext(), errorMessage, Toast.LENGTH_LONG).show();
    }


}