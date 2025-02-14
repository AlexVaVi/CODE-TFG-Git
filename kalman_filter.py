# kalman_filter.py
import numpy as np
from conversion import latlon_to_xy, xy_to_latlon
from distance_to_infra import distance_to_infra

def kalman_filter(latitudes, longitudes, vx, vy, ref_lat, ref_lon):
    """
    Applies a Kalman filter (constant velocity model) that:
      - If the measured point is closer to a runway, it updates the state with the normal measurement
        (position and velocity, 4 dimensions).
      - If the point is closer to a taxiway and is within a threshold, a constraint is applied that forces
        the distance to the taxiway to 0 (5-dimensional update).
    
    The conversion from lat/lon to a local coordinate system (x, y in meters) is performed using a reference point
    (ref_lat, ref_lon). Noise parameters should be adjusted according to the scale of your data.
    
    Returns:
      corrected_lat, corrected_lon: arrays with the corrected trajectory (in degrees).
    """
    n = len(latitudes)
    # Convert the original positions to meters
    x, y = latlon_to_xy(latitudes, longitudes, ref_lat, ref_lon)
    
    # Initial state: [x, y, vx, vy]
    X_estimate = np.zeros((n, 4))
    X_estimate[0] = [x[0], y[0], vx[0], vy[0]]
    
    # Initialize the covariance for each time step (4x4)
    P_estimate = np.zeros((n, 4, 4))
    P_estimate[0] = np.eye(4) * 10.0  # Adjust according to initial uncertainty
    
    dt = 1.0
    # Transition matrix (constant velocity model)
    A = np.array([[1, 0, dt, 0],
                  [0, 1, 0, dt],
                  [0, 0, 1,  0],
                  [0, 0, 0,  1]])
    
    # Process noise (acceleration uncertainty, in m/s²)
    ax = 1.0
    ay = 1.0
    w = np.array([[ax * (dt**2) / 2],
                  [ay * (dt**2) / 2],
                  [ax * dt],
                  [ay * dt]])
    Q = w @ w.T  # 4x4 matrix
    
    # Measurement noise parameters (in meters and m/s)
    sigmax  = 5.0    # uncertainty in x (m)
    sigmay  = 5.0    # uncertainty in y (m)
    sigmavx = 1.0    # uncertainty in vx (m/s)
    sigmavy = 1.0    # uncertainty in vy (m/s)
    epsilon = 10.0   # uncertainty for the constraint (m)
    
    # Measurement matrices:
    # For normal update (no constraint): dimension 4
    R_4 = np.diag([sigmax**2, sigmay**2, sigmavx**2, sigmavy**2])
    # For update with constraint (dimension 5)
    R_5 = np.diag([sigmax**2, sigmay**2, sigmavx**2, sigmavy**2, epsilon**2])
    
    # Threshold for applying the constraint (in meters)
    constraint_threshold = 50.0
    
    for k in range(1, n):
        # --- Prediction ---
        X_pred = A @ X_estimate[k-1]
        P_pred = A @ P_estimate[k-1] @ A.T + Q
        
        # --- Evaluate the distance to the infrastructure ---
        # The function distance_to_infra is used to compare taxiways and runways.
        # It returns (infra_type, distance, dphi_dx, dphi_dy)
        infra_type, distance_estimated, dphi_dx, dphi_dy = distance_to_infra(
            X_pred[0], X_pred[1], ref_lat, ref_lon)
        
        if infra_type == 'runway':
            # If the point is closer to a runway, NO constraint is applied.
            # Update is done in 4 dimensions.
            x_meas, y_meas = latlon_to_xy([latitudes[k]], [longitudes[k]], ref_lat, ref_lon)
            z = np.array([
                [x_meas[0]],
                [y_meas[0]],
                [vx[k]],
                [vy[k]]
            ])
            z_pred = np.array([
                [X_pred[0]],
                [X_pred[1]],
                [X_pred[2]],
                [X_pred[3]]
            ])
            v_innov = z - z_pred
            H = np.eye(4)
            S = H @ P_pred @ H.T + R_4
            K = P_pred @ H.T @ np.linalg.inv(S)
            
            X_estimate[k] = (X_pred.reshape(4, 1) + K @ v_innov).flatten()
            P_estimate[k] = (np.eye(4) - K @ H) @ P_pred
            
        else:
            # If the point is closer to a taxiway, the constraint is applied.
            # The distance to the taxiway is corrected to 0 only if the distance is smaller than the threshold.
            if distance_estimated > constraint_threshold:
                # If it's far from the taxiway, the constraint is ignored:
                H_constraint = np.array([0, 0, 0, 0])
                z_constraint = np.array([[distance_estimated]])
            else:
                H_constraint = np.array([dphi_dx, dphi_dy, 0, 0])
                z_constraint = np.array([[0]])
                
            x_meas, y_meas = latlon_to_xy([latitudes[k]], [longitudes[k]], ref_lat, ref_lon)
            z = np.array([
                [x_meas[0]],
                [y_meas[0]],
                [vx[k]],
                [vy[k]],
                z_constraint[0]
            ])
            z_pred = np.array([
                [X_pred[0]],
                [X_pred[1]],
                [X_pred[2]],
                [X_pred[3]],
                [distance_estimated]
            ])
            v_innov = z - z_pred
            # 5x4 observation matrix:
            # First 4 rows: identity; fifth row: H_constraint
            H = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                H_constraint
            ])
            S = H @ P_pred @ H.T + R_5
            K = P_pred @ H.T @ np.linalg.inv(S)
            
            X_estimate[k] = (X_pred.reshape(4, 1) + K @ v_innov).flatten()
            P_estimate[k] = (np.eye(4) - K @ H) @ P_pred
    
    # Convert the corrected trajectory from x, y (meters) back to lat, lon (degrees)
    corrected_lat, corrected_lon = xy_to_latlon(X_estimate[:, 0], X_estimate[:, 1], ref_lat, ref_lon)
    return corrected_lat, corrected_lon