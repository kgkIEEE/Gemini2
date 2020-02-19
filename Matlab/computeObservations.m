% For a specific satellite and ground station
% determine visibilities during some period

% Satellite data is stored in the "satdata" array 
% of structures

% Ground station location
D2R = pi/180.;
R2D = 180./pi;
groundStation.latitude = 8.7*D2R; % radians
groundStation.longitude = 167.0*D2R; % radian
groundStation.altitude = 0.1; % kilometers


% Observation period
startObs = juliandate(datetime("01-Jan-2020 00:00:00"));
endObs = juliandate(datetime("02-Jan-2020 00:00:00"));

timeStep = 0.0001; % About 8.6 seconds

% Time is in Julian day format
time = startObs;
obsCount = 0;
above = 0;
while (time < endObs)
    [satPos, satVel] = computeSatPosVel(time, satdata(1));
    [az, el, range] = computeLookAngle(time, satPos, groundStation);
    if el > 0.
        above = 1;
        obsCount = obsCount + 1;
        observation(obsCount).time = time;
        observation(obsCount).az = az;
        observation(obsCount).el = el;
        observation(obsCount).range = range;
        fprintf('%16.5f %12.5f %7.2f %7.2f %12.3f %12.3f %12.3f %12.3f\n', ...
            time, time-startObs, az*R2D, el*R2D, range, ...
            satPos(1), satPos(2), satPos(3));
    else
        if above > 0
            fprintf('\n');
            above = 0;
        end
    end

    time = time + timeStep;
end
