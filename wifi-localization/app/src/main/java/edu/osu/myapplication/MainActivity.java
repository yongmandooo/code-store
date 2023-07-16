package edu.osu.myapplication;

import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.util.TreeMap;
import java.util.Vector;

public class MainActivity extends AppCompatActivity {
    private final String TAG = this.getClass().getSimpleName();
    private boolean wd_mode = false;
    private boolean is_localizing = false;
    ImageView imageview;
    static View currentMarker;
    float mX = -1;
    float mY = -1;
    IntentFilter mIntentFilter;
    WifiManager mWifiManager;
    List<ScanResult> scanResults;

    public class Position {
        private float xPos;
        private float yPos;

        Position(float x, float y) {
            this.xPos = x;
            this.yPos = y;
        }

        float getXPos() {
            return xPos;
        }

        float getYPos() {
            return yPos;
        }
    }

    HashMap<Position, HashMap<String, Integer>> locAPTable = new HashMap<>();
    List<ImageView> savedPositionMarkers = new ArrayList<>();

    static final int PERMISSIONS_REQUEST = 0x0000001;

    @Override
    @SuppressLint("ClickableViewAccessibility")
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        onCheckPermission();

        mIntentFilter = new IntentFilter();
        mWifiManager = (WifiManager) getSystemService(Context.WIFI_SERVICE);

        imageview = findViewById(R.id.imageView);
        Intent intent = new Intent();
        ConstraintLayout scan_layout = findViewById(R.id.scanConstraintLayout);
        FrameLayout imageFrame = findViewById(R.id.imageFrame);
        View marker = findViewById(R.id.marker);
        currentMarker = findViewById(R.id.green_marker);
        marker.bringToFront();
        View scanResultView = findViewById(R.id.scan_result_layout);

        Button gallery = findViewById(R.id.gallery);
        Button war_driving = findViewById(R.id.war_driving);
        Button localization = findViewById(R.id.localization);
        war_driving.setVisibility(View.GONE);
        localization.setVisibility(View.GONE);

        gallery.setOnClickListener(v -> {
            if (imageview.getDrawable() == null) {
                intent.setType("image/*");
                intent.setAction(Intent.ACTION_GET_CONTENT);
                launcher.launch(intent);
                gallery.setText(R.string.Delete_map);
                war_driving.setVisibility(View.VISIBLE);
                war_driving.setEnabled(true);
            } else {
                imageview.setImageDrawable(null);
                gallery.setText(R.string.Upload_map);
                war_driving.setVisibility(View.GONE);
                war_driving.setEnabled(false);
                scan_layout.setVisibility(View.GONE);
                marker.setVisibility(View.GONE);
                locAPTable = null;
                locAPTable = new HashMap<>();
                savedPositionMarkers = null;
                savedPositionMarkers = new ArrayList<>();
            }
        });

        war_driving.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                wd_mode = !wd_mode;
                if (wd_mode) {
                    scan_layout.setVisibility(View.VISIBLE);
                    gallery.setVisibility(View.GONE);
                    war_driving.setText("EXIT");
                    if (savedPositionMarkers != null) {
                        for (ImageView iv : savedPositionMarkers) {
                            iv.setVisibility(View.VISIBLE);
                        }
                    }
                    if (locAPTable != null) {
                        setLocalizationBtn(localization, new ArrayList<>(locAPTable.keySet()));
                    }
                    imageview.setOnTouchListener((view, motionEvent) -> {
                        mX = motionEvent.getX();
                        mY = motionEvent.getY();
                        marker.setVisibility(View.VISIBLE);
                        marker.setX(mX);
                        marker.setY(mY);
                        return true;
                    });
                } else {
                    scan_layout.setVisibility(View.GONE);
                    gallery.setVisibility(View.VISIBLE);
                    war_driving.setText("WAR DRIVING");
                    if (savedPositionMarkers != null) {
                        for (ImageView iv : savedPositionMarkers) {
                            iv.setVisibility(View.GONE);
                        }
                    }
                    localization.setVisibility(View.GONE);
                    marker.setVisibility(View.GONE);
                    is_localizing = false;
                    imageview.setOnTouchListener(new View.OnTouchListener() {
                        @Override
                        public boolean onTouch(View view, MotionEvent motionEvent) {
                            return false;
                        }
                    });
                }
            }
        });

        Button scanButton = findViewById(R.id.scan);
        scanButton.setOnClickListener(v -> {
            if (mX > 0 && mY > 0) {
                imageview.setVisibility(View.GONE);
                scan_layout.setVisibility(View.GONE);
                war_driving.setVisibility(View.GONE);
                scanResultView.setVisibility(View.VISIBLE);
                scanResultView.bringToFront();
                boolean scanStarted = mWifiManager.startScan();

                if (!scanStarted) Log.e(TAG, "Wifi scan failed");
            }
        });

        mIntentFilter.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);

        Button scanYes = findViewById(R.id.save_scan_result_yes);
        scanYes.setOnClickListener(v -> {
            if (scanResults != null) {
                imageview.setVisibility(View.VISIBLE);
                scan_layout.setVisibility(View.VISIBLE);
                war_driving.setVisibility(View.VISIBLE);
                scanResultView.setVisibility(View.GONE);

                HashMap<String, Integer> apInfo = new HashMap<>();
                for (ScanResult result : scanResults) {
                    apInfo.put(result.BSSID, result.level);
                }
                Position pos = new Position(mX, mY);
                locAPTable.put(pos, apInfo);
                System.out.println("테이블 사이즈 " + locAPTable.values());

                if (wd_mode && locAPTable != null) {
                    List<Position> positionList = new ArrayList<>(locAPTable.keySet());
                    System.out.println("저장된 위치들 "+positionList.size());
                    for (Position savedPosition : positionList) {
                        ImageView redMarker = new ImageView(this);
                        redMarker.setLayoutParams(new ViewGroup.
                                LayoutParams(FrameLayout.LayoutParams.WRAP_CONTENT,
                                FrameLayout.LayoutParams.WRAP_CONTENT));
                        redMarker.setImageResource(R.drawable.red_marker);
                        imageFrame.addView(redMarker);
                        redMarker.setX(savedPosition.getXPos());
                        redMarker.setY(savedPosition.getYPos());
                        savedPositionMarkers.add(redMarker);
                    }
                    setLocalizationBtn(localization, positionList);
                }
                marker.setVisibility(View.GONE);
                mX = -1;
                mY = -1;
            }
        });

        Button scanNo = findViewById(R.id.save_scan_result_no);
        scanNo.setOnClickListener(v -> {
            imageview.setVisibility(View.VISIBLE);
            scan_layout.setVisibility(View.VISIBLE);
            war_driving.setVisibility(View.VISIBLE);
            scanResultView.setVisibility(View.GONE);
        });

        localization.setOnClickListener(v -> {
            is_localizing = !is_localizing;
            if (is_localizing) {
                localization.setText("stop localizing");
                currentMarker.setVisibility(View.VISIBLE);
                currentMarker.bringToFront();
                MyHandler handler = new MyHandler();
                new Thread((new Runnable() {
                    @Override
                    @SuppressWarnings("MissingPermission")
                    //Localization Process
                    //------------------------------------------------------------------------------
                    public void run() {
                        //locAPTable 기반 위치 찾아서 마커 표시
                        //현재 AP 스캔 결과를 hashmap으로 구성
                        List<ScanResult> currentScanResult = mWifiManager.getScanResults();
                        HashMap<String, Integer> currentPosAPInfo = new HashMap<>();
                        for (ScanResult result : currentScanResult) {
                            currentPosAPInfo.put(result.BSSID, result.level);
                        }
                        //최소 거리의 AP 스캔 포인트 계산
                        double minDistance = Double.MAX_VALUE;
                        HashMap<String, Integer> minAPScanPoint = new HashMap<>();
                        List<String> currentPosAPIds = new ArrayList<>(currentPosAPInfo.keySet());
                        for (HashMap<String, Integer> apInfoList : locAPTable.values()) {

                            List<Integer> distanceVector = new ArrayList<>();
                            for (String id : currentPosAPIds) {
                                if (apInfoList.keySet().contains(id)) {
                                    distanceVector.add(currentPosAPInfo.get(id) - apInfoList.get(id));
                                }
                            }

                            double disSq = 0;
                            for (Integer v : distanceVector) {
                                disSq += v * v;
                            }
                            double distance = Math.sqrt(disSq);
                            distance = distance / distanceVector.size();

                            if (distance < minDistance) {
                                minDistance = distance;
                                minAPScanPoint = apInfoList;
                            }
                        }
                        //current marker 표시하고 position 설정
                        Position findKey = null;
                        for (Position pos : locAPTable.keySet()) {
                            if (locAPTable.get(pos).equals(minAPScanPoint)) {
                                findKey = pos;
                            }
                        }
                        if (findKey != null) {
                            Message m = handler.obtainMessage();
                            Bundle bundle = new Bundle();
                            bundle.putFloat("Xpos", findKey.getXPos());
                            bundle.putFloat("Ypos", findKey.getYPos());
                            m.setData(bundle);
                            handler.sendMessage(m);
                        }
                        handler.postDelayed(this, 1000);
                    }
                    //------------------------------------------------------------------------------
                    //Localization Process End
                })).start();
            } else {
                localization.setText("localization");
                currentMarker.setVisibility(View.GONE);
            }
        });
    }

    public static class MyHandler extends Handler {
        @Override
        public void handleMessage(Message msg){
            super.handleMessage(msg);

            Bundle bundle = msg.getData();
            currentMarker.setX(bundle.getFloat("Xpos"));
            currentMarker.setY(bundle.getFloat("Ypos"));
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        registerReceiver(mReceiver, mIntentFilter);
    }

    @Override
    protected void onPause() {
        super.onPause();
        unregisterReceiver(mReceiver);
    }
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        switch (requestCode) {
            case PERMISSIONS_REQUEST: {

                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Log.d("permission","권한 획득 성공");

                } else {
                    Log.d("permission","권한 획득 실패");
                }
                return;
            }

        }
    }

    public void onCheckPermission() {
        if (ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.ACCESS_WIFI_STATE) != PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.CHANGE_WIFI_STATE) != PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.ACCESS_NETWORK_STATE) != PackageManager.PERMISSION_GRANTED
                || ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.INTERNET) != PackageManager.PERMISSION_GRANTED) {

                ActivityCompat.requestPermissions(MainActivity.this,
                        new String[]{Manifest.permission.ACCESS_COARSE_LOCATION,
                                Manifest.permission.ACCESS_FINE_LOCATION,
                                Manifest.permission.ACCESS_WIFI_STATE,
                                Manifest.permission.CHANGE_WIFI_STATE,
                                Manifest.permission.ACCESS_NETWORK_STATE,
                                Manifest.permission.INTERNET},
                        PERMISSIONS_REQUEST);
        }
    }

    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        @SuppressWarnings("MissingPermission")
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (WifiManager.SCAN_RESULTS_AVAILABLE_ACTION.equals(action)) {
                Log.e(TAG, "Scan results available");
                scanResults = mWifiManager.getScanResults();
                String mApStr = "";
                for (ScanResult result : scanResults){
                    mApStr = mApStr + result.SSID + "; ";
                    mApStr = mApStr + result.BSSID + "; ";
                    mApStr = mApStr + result.capabilities + "; ";
                    mApStr = mApStr + result.frequency + " MHz;";
                    mApStr = mApStr + result.level + " dBm\n\n";
                }
                setTextView(mApStr);
            }
        }
    };

    private void setTextView(String str){
        TextView resultview = findViewById(R.id.scan_result);
        resultview.setMovementMethod(new ScrollingMovementMethod());
        resultview.setText(str);
    }

    private void setLocalizationBtn(Button btn, List<Position> list){
        if(list.size() >= 10){
            btn.setVisibility(View.VISIBLE);
        }else{
            btn.setVisibility(View.GONE);
        }
    }

    ActivityResultLauncher<Intent> launcher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
            new ActivityResultCallback<ActivityResult>()
            {
                @Override
                public void onActivityResult(ActivityResult result)
                {

                    Intent intent = result.getData();
                    Uri uri = intent.getData();
                    if (result.getResultCode() == RESULT_OK && uri != null)
                    {
                        Log.e(TAG, "result : " + result);
                        Log.e(TAG, "intent : " + intent);
                        Log.e(TAG, "uri : " + uri);
                        imageview.setImageURI(uri);
                    }
                }
            });
}