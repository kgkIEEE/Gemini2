% For a specific satellite and ground station
% determine visibilities during some period

% Satellite data is stored in the "satdata" array 
% of structures

% Ground station location
D2R = pi/180.;
groundStation.latitude = 10.*D2R; % radians
groundStation.longitude = 90.*D2R; % radian
groundStation.altitude = 0.1; % kilometers


% Observation period
startObs = juliandate(datetime("01-Jan-2020 00:00:00"));
endObs = juliandate(datetime("02-Jan-2020 00:00:00"));

timeStep = 0.001; % About 86 seconds

% Time is in Julian day format
time = startObs;
obsCount = 0;
while (time < endObs)
    [satPos, satVel] = computeSatPosVel(time, satdata(1));
    [az, el, range] = computeLookAngle(time, satPos, groundStation);
    if el > 0.
        obsCount = obsCount + 1;
        observation(obsCount).time = time;
        observation(obsCount).az = az;
        observation(obsCount).el = el;
        observation(obsCount).range = range;
    end
    time = time + timeStep;
end
print(obsCount)        
        
    