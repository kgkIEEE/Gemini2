function [pos, vel] = computeSatPosVel(time, satdata)
    minutesPerDay = 1440.;
    % Compute difference between requested time
    % and TLE epoch
    deltaTime = time - convertTleEpochToJdate(satdata.epoch);
    % SGP4 delta time is in minutes
    % There are 1440 minutes per day
    tsince = deltaTime * minutesPerDay;
    [pos, vel ] = sgp4(tsince,satdata);
end