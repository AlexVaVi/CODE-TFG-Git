# kalman_filter.py
import numpy as np
from conversion import latlon_to_xy, xy_to_latlon
from distance_to_infra import distance_to_infra
from shapely.geometry import Point, LineString
import pandas as pd
from ApronAnalysis import find_apron

def kalman_filter(df_flight, ref_lat, ref_lon):

    # max_distance = 30
    
    df_apron = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')
    df_apron = df_apron[df_apron['type'] == 'apron']

    # Arlanda Airport nodes divided by segments
    df = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')
    # flight = df_flight[(df_flight['callsign_group'] == callsign_nr) & (df_flight['onground'] == True)].copy()
    callsign = df_flight['callsign'].unique()[0]
    
    # ref_lat = df_flight['latitude'].values[0]
    # ref_lon = df_flight['longitude'].values[0]

    x, y = latlon_to_xy(df["latitude"].values, df["longitude"].values, ref_lat, ref_lon)
    df["x"] = x
    df["y"] = y

    linestrings = {}
    for (way_type, way_id), group in df.groupby(["type", "way_id"]):
        points = [Point(row["x"], row["y"]) for _, row in group.iterrows()]
        if len(points) >= 2:
            line = LineString(points)
            linestrings[(way_type, way_id)] = line
    


    df_flight['latitude'] = df_flight['latitude'].astype(float)
    df_flight['longitude'] = df_flight['longitude'].astype(float)
    df_flight['groundspeed'] = df_flight['groundspeed'].astype(float)
    df_flight['track'] = np.radians(df_flight['track'].astype(float))
    
    vx = df_flight['groundspeed'].values * np.cos(df_flight['track'].values)
    vy = df_flight['groundspeed'].values * np.sin(df_flight['track'].values)
    
    latitudes = df_flight['latitude'].values
    longitudes = df_flight['longitude'].values
    
    n = len(latitudes)
    # # Convert the original positions to meters
    x, y = latlon_to_xy(latitudes, longitudes, ref_lat, ref_lon)
    
    # print(x[0], y[0], vx[1], vy[1])
    
    # # Initial state: [x, y, vx, vy]
    X_estimate = np.zeros((n, 4))
    X_estimate[0] = [x[0], y[0], vx[0], vy[0]]
    
    # # Initialize the covariance for each time step (4x4)
    # P_estimate = np.zeros((n, 4, 4))
    # P_estimate[0] = np.eye(4) * 10.0  # Adjust according to initial uncertainty
    
    # dt = 0.0
    # # Transition matrix (constant velocity model)
    # A = np.array([[1, 0, dt, 0],
    #               [0, 1, 0, dt],
    #               [0, 0, 1,  0],
    #               [0, 0, 0,  1]])
    
    # # Process noise (acceleration uncertainty, in m/s²)
    # ax = 1.0
    # ay = 1.0
    # w = np.array([[ax * (dt**2) / 2],
    #               [ay * (dt**2) / 2],
    #               [ax * dt],
    #               [ay * dt]])
    # Q = w @ w.T  # 4x4 matrix
    
    # # Measurement noise parameters (in meters and m/s)
    # sigmax  = 5.0    # uncertainty in x (m)
    # sigmay  = 5.0    # uncertainty in y (m)
    # sigmavx = 1.0    # uncertainty in vx (m/s)
    # sigmavy = 1.0    # uncertainty in vy (m/s)
    # epsilon = 10.0   # uncertainty for the constraint (m)
    
    # # Measurement matrices:
    # # For normal update (no constraint): dimension 4
    # R_4 = np.diag([sigmax**2, sigmay**2, sigmavx**2, sigmavy**2])
    # # For update with constraint (dimension 5)
    # R_5 = np.diag([sigmax**2, sigmay**2, sigmavx**2, sigmavy**2, epsilon**2])
    
    # Threshold for applying the constraint (in meters)
    threshold = 50.0
    
    closest_segments = []
    unique_segments = []
    prev_seg = None

    for k in range(0, n):
        # --- Prediction ---
        # X_pred = A @ X_estimate[k-1]
        # P_pred = A @ P_estimate[k-1] @ A.T + Q
        
        # Pred_point = Point(X_pred[0], X_pred[1])
        Pred_point2 = Point(x[k], y[k])
        
        if find_apron(latitudes[k], longitudes[k] , df_apron) is not None:
            X_estimate[k] = [x[k], y[k], vx[k], vy[k]]
            continue
        
        else:
          min_distance = float("inf")
          closest_segment = None
          for key, segment in linestrings.items():
              dist = Pred_point2.distance(segment)
              if dist < min_distance:
                  min_distance = dist
                  closest_segment = segment
      
          # print(closest_segment)
          
          # if min_distance > max_distance:
          #     x_meas, y_meas = latlon_to_xy([latitudes[k]], [longitudes[k]], ref_lat, ref_lon)
          #     X_estimate[k] = [x_meas[0], y_meas[0], vx[k], vy[k]]
          #     P_estimate[k] = P_estimate[k-1]
          #     continue
          
          dist_along_segmentMeasured = closest_segment.project(Point(X_estimate[k-1][0], X_estimate[k-1][1]))
          dist_along_segment = closest_segment.project(Pred_point2)
          closest_point = closest_segment.interpolate(dist_along_segment)
          
          min_distance = float("inf")
          closest_segment = None
          for key, segment in linestrings.items():
              dist = Pred_point2.distance(segment)
              if dist < min_distance:
                  min_distance = dist
                  closest_segment = segment
          
          if prev_seg is None or closest_segment != prev_seg:
              closest_segments.append(closest_segment)
              prev_seg = closest_segment
          
          # # print(f"Punt mes proper: {closest_point.x}, {closest_point.y}")
          
          # dx = Pred_point.x - closest_point.x
          # dy = Pred_point.y - closest_point.y

          # phi = (dx**2 + dy**2)**0.5  

          # if phi != 0:
          #     dphi_dx = dx / phi
          #     dphi_dy = dy / phi
          # else:
          #     dphi_dx = 0
          #     dphi_dy = 0
          
          # # --- Update ---
          # # The update depends on the distance to the infrastructure        
          # if dist_along_segment > threshold:
          #     H_constraint = np.array([0, 0, 0, 0])
          #     z_constraint = dist_along_segmentMeasured
          #     z_constraint_pred = dist_along_segment
          # else:
          #     H_constraint = np.array([dphi_dx, dphi_dy, 0, 0])
          #     z_constraint = 0
          #     z_constraint_pred = dist_along_segment       
          
          # x_meas_list = []
          # y_meas_list = []
          # x_meas, y_meas = latlon_to_xy([latitudes[k]], [longitudes[k]], ref_lat, ref_lon)
          # x_meas_list.append(x_meas[0])  # Extrae escalar y guarda
          # y_meas_list.append(y_meas[0])  # Extrae escalar y guarda
      
          # z = np.array([
          #         [x_meas[0]],
          #         [y_meas[0]],
          #         [vx[k]],
          #         [vy[k]],
          #         [z_constraint]
          #     ])
          # z_pred = np.array([
          #         [X_pred[0]],
          #         [X_pred[1]],
          #         [X_pred[2]],
          #         [X_pred[3]],
          #         [z_constraint_pred]
          #     ])
          # v_innov = z - z_pred
          #     # 5x4 observation matrix:
          #     # First 4 rows: identity; fifth row: H_constraint
          # H = np.array([
          #         [1, 0, 0, 0],
          #         [0, 1, 0, 0],
          #         [0, 0, 1, 0],
          #         [0, 0, 0, 1],
          #         H_constraint
          #     ])
          # S = H @ P_pred @ H.T + R_5
          # K = P_pred @ H.T @ np.linalg.inv(S)
              
          # X_estimate[k] = (X_pred.reshape(4, 1) + K @ v_innov).flatten()
          # P_estimate[k] = (np.eye(4) - K @ H) @ P_pred
          
          X_estimate[k] = (closest_point.x, closest_point.y, X_estimate[k][2], X_estimate[k][3])

    # Convert the corrected trajectory from x, y (meters) back to lat, lon (degrees)
    corrected_lat, corrected_lon = xy_to_latlon(X_estimate[:, 0], X_estimate[:, 1], ref_lat, ref_lon)
    
    return corrected_lat, corrected_lon, closest_segments

    
