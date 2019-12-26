% Look angle from ground observer to satellite
radiusEarth = 6371.0; % km
satelliteRadius = radiusEarth + 1000.0;
G = 6.67408e-11;
D2R = pi/180.;
R2D = 1.0/D2R;
% Sidereal Day Length is 23:56:04.09054
siderealDayLength = 23*3600 + 56*60 + 4.09054; % in seconds


SATELLITE_INCLINATION = 45. * D2R;
OBSERVER_LATITUDE = 30. * D2R;
OBSERVER_LONGITUDE = 90. * D2R;
OBSERVER_ALTITUDE = 0.;

% Observer location
latitude = OBSERVER_LATITUDE;
longitude = OBSERVER_LONGITUDE;
altitude = OBSERVER_ALTITUDE;

% A more accurate calculation involves 
% the oblateness of the Earth
R = radiusEarth * cos(latitude);
x = R * cos(longitude);
y = R * sin(longitude);
z = radiusEarth * sin(latitude);
observerECF = [x y z];

% Compute Julian Date at start
timeStart = computeJulianDate("23-Dec-2019 20:20:24");

% Compute Greenwich Mean Sidereal Time (GMST) at start
gmst = computeGMST(timeStart);

% Satellite in a circular orbit around the Earth
count = 4000;
satellite = zeros(count, 2);
time = zeros(count,1);
range = zeros(count, 1);
elevation = zeros(count, 1);
azimuth = zeros(count, 1);

w = 2*pi/count;
for t = 1:count
    x = satelliteRadius*[cos(w*t) sin(w*t)];
    satellite(t,:) = satelliteRadius*[sin(w*t) cos(w*t)];
end

% Note: the X direction in this frame of reference points towards
% a distant star in the constellation Aries.  This star is 
% known as the first point of Aries

% When working with Earth, the Z direction is aligned with the 
% axis of rotation, or the line that goes through the North and 
% South Poles

% When working with interplanetary travel we shift the frame of 
% reference to be centered on the Sun and use its axis of 
% rotation, which differs from the Earth's by a few degrees

% Satellite in a circular orbit with a 45 degree inclination
satellite3d = zeros(count,3);
% Use an orbital period of 90 minutes
w = 2*pi/90;

inclination = SATELLITE_INCLINATION;
cosInc = cos(inclination);
sinInc = sin(inclination);

% To compensate for the addition of the 3 matrices
scale = 1.0/3.0;

rotX = scale*[ 1 0 0; 0 cosInc -sinInc; 0 sinInc cosInc];
rotY = scale*[cosInc 0 sinInc; 0 1 0; -sinInc 0 cosInc];
rotZ = scale*[cosInc -sinInc 0; sinInc cosInc 0; 0 0 1];

% Compute the ECI position of the satellite over time
% Time step in minutes
for t = 1:count
    satellite3d(t,:) = rotX * [satellite(t,1); satellite(t,2); 0] + ...
        rotY * [satellite(t,1); satellite(t,2); 0] + ...
        rotZ * [satellite(t,1); satellite(t,2); 0];
    time(t) = 1.0/1440.; % Simulation time in fraction of a day
end

figure('Name','Satellite Orbit');
plot3(satellite3d(:,1),satellite3d(:,2),satellite3d(:,3));

% Compute the ECI position of the ground observer over time
observer3d = zeros(count,3);
latitude = 0.0 * D2R;
longitude = 0.0;
wEarth = 2*pi/1440.0;
for t = 1:count
    observer3d(t,:) = radiusEarth*[cos(wEarth*t); sin(wEarth*t); ...
        sin(latitude)];
end

figure('Name','Satellite and Observer');
plot3(satellite3d(:,1),satellite3d(:,2),satellite3d(:,3), ...
    observer3d(:,1), observer3d(:,2), observer3d(:,3));

% Compute look angle between observer and satellite
for t=1:count
    delta(t,:) = ...
        [satellite3d(t,1) - observer3d(t,1); ...
        satellite3d(t,2) - observer3d(t,2); ...
        satellite3d(t,3) - observer3d(t,3)];
    theta = mod((gmst + longitude + time(t)/siderealDayLength), 2*pi);
    [az(t), el(t), range(t)] = computeLookAngle( ...
        delta(t,1),delta(t,2),delta(t,3), ...
        latitude, theta);
end

figure('Name','Vector difference between satellite and observer');
plot3(delta(:,1),delta(:,2),delta(:,3));
figure('Name','Angle between satellite and observer');
plot(elevation);
figure('Name','Distance between observer and satellite');
plot(range);

function jDate = computeJulianDate(dateTimeString)
    % Date and Time at start of this simulation
    jDate = juliandate(datetime(dateTimeString));
end

function gmst = computeGMST(jDate)

    % Compute Julian Date
    % Jan 1, 2000 Julian Date is 2,451,544.5
    Tu = (jDate - 2451545.0)/36525; % UT elapsed since 1/1/2000 at noon

    % Compute Greenwich Mean Sidereal Time (GMST)
    % The higher powers of Tu account for the variation in the
    % rotation rate of the Earth
    gmst = 24110.5484 + 8640184.812866*Tu + 0.093104*power(Tu,2) - ...
        6.2e-6*power(Tu,3);
    % Check: impact of the higher power variations of Tu
    rotationalVariation = 0.093104*power(Tu,2) - ...
        6.2e-6*power(Tu,3);
end

function [az, el, rg] = computeLookAngle(x,y,z,lat,theta)
    top_s = x*sin(lat)*cos(theta) + ...
        y*sin(lat)*sin(theta) - ...
        z*cos(lat);
    top_e = -x*sin(theta) + ...
        y*cos(theta);
    top_z = x*cos(lat)*cos(theta) + ...
        y*cos(lat)*sin(theta) + ...
        z*sin(lat);
    az = atan2(-top_e, top_s);
    rg = norm([x y z]);
    el = asin(top_z/rg);
end





