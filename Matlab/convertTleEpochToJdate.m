% Convert TLE epoch to Julian date
% TLE epoch format is last 2 digits of year*1000 and
% day of year.  Jan 1 2019 is 19000.00000, 
% Dec 31 2019 at noon is 19364.50000
function jDate = convertTleEpochToJdate(epoch)
    epochYear = fix(epoch/1000);
    % Y2K-like kluge
    if epochYear < 80
        epochYear = epochYear + 2000;
    else
        epochYear = epochYear + 1900;
    end
    jDate = juliandate(datetime(epochYear,1,1)) + mod(epoch,1000);
end
    
