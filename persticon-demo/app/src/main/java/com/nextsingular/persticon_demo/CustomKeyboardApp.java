package com.nextsingular.persticon_demo;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.inputmethodservice.InputMethodService;
import android.net.Uri;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.ScrollView;

import androidx.core.content.FileProvider;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.Field;

public class CustomKeyboardApp extends InputMethodService {

    @Override
    public View onCreateInputView() {

        LinearLayout keyboardView = (LinearLayout) getLayoutInflater().inflate(R.layout.custom_keyboard_layout, null);

        ImageView imgKey1 = (ImageView) keyboardView.findViewById(R.id.imgKey1);
        imgKey1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //how img btn works
                ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);

                Bitmap sendBitmap = BitmapFactory.decodeResource(getResources(), R.raw.momil1);
                ByteArrayOutputStream stream = new ByteArrayOutputStream();
                sendBitmap.compress(Bitmap.CompressFormat.PNG, 100, stream);
                byte[] byteArray = stream.toByteArray();
                File imageFile = saveImageToFile(byteArray);

                Uri imageUri = FileProvider.getUriForFile(getApplicationContext(),
                        getApplicationContext().getPackageName() + ".fileprovider", imageFile);

                ClipData clip = ClipData.newUri(getContentResolver(), "Image", imageUri);

                clipboard.setPrimaryClip(clip);
                Log.d("success check", "onclick method succeed");
            }
        });

        return keyboardView;
    }

    // Save the image data to a file using FileProvider
    private File saveImageToFile(byte[] imageData) {
        try {
            File directory = new File(getFilesDir(), "images");
            if (!directory.exists()) {
                directory.mkdirs();
            }

            File file = new File(directory, "image.png");
            FileOutputStream fos = new FileOutputStream(file);
            fos.write(imageData);
            fos.close();
            return file;
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }
}
