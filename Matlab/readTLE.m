clc
clear
format long g

ge = 398600.8; % Earth gravitational constant
TWOPI = 2*pi;
MINUTES_PER_DAY = 1440.;
MINUTES_PER_DAY_SQUARED = (MINUTES_PER_DAY * MINUTES_PER_DAY);
MINUTES_PER_DAY_CUBED = (MINUTES_PER_DAY * MINUTES_PER_DAY_SQUARED);

count = 0;

% TLE file name 
fnameDefault = 'catalog.txt';
fname = fnameDefault;

fileID = fopen('tle.txt','w');

% Open the TLE file and read TLE elements
fid = fopen(fname, 'r');
% exit if file open fails


% 19-32	04236.56031392	Element Set Epoch (UTC)
%   the format of the epoch is (year modulo 100)*1000 + day of year
% 3-7	25544	Satellite Catalog Number
% 9-16	51.6335	Orbit Inclination (degrees)
% 18-25	344.7760	Right Ascension of Ascending Node (degrees)
% 27-33	0007976	Eccentricity (decimal point assumed)
% 35-42	126.2523	Argument of Perigee (degrees)
% 44-51	325.9359	Mean Anomaly (degrees)
% 53-63	15.70406856	Mean Motion (revolutions/day)
% 64-68	32890	Revolution Number at Epoch

while (1)
    % read first line
    tline = fgetl(fid);
    if ~ischar(tline)
        break
    end
    Cnum = tline(3:7);      			        % Catalog Number (NORAD)
    objnumber = str2num(Cnum);
    SC   = tline(8);					        % Security Classification
    ID   = tline(10:17);			            % Identification Number
    epoch = str2num(tline(19:32));              % Epoch
    TD1   = str2num(tline(34:43));              % first time derivative
    TD2   = str2num(tline(45:50));              % 2nd Time Derivative
    ExTD2 = tline(51:52);                       % Exponent of 2nd Time Derivative
    BStar = str2num(tline(54:59));              % Bstar/drag Term
    ExBStar = str2num(tline(60:61));            % Exponent of Bstar/drag Term
    BStar = BStar*1e-5*10^ExBStar;
    Etype = tline(63);                          % Ephemeris Type
    Enum  = str2num(tline(65:end));             % Element Number
    
    % read second line
    tline = fgetl(fid);
    if ~ischar(tline)
        break
    end
    incl = str2num(tline(9:16));                   % Orbit Inclination (degrees)
    raan = str2num(tline(18:25));               % Right Ascension of Ascending Node (degrees)
    e = str2num(strcat('0.',tline(27:33)));     % Eccentricity
    omega = str2num(tline(35:42));              % Argument of Perigee (degrees)
    M = str2num(tline(44:51));                  % Mean Anomaly (degrees)
    no = str2num(tline(53:63));                 % Mean Motion
    a = ( ge/(no*2*pi/86400)^2 )^(1/3);         % semi major axis (m)
    rNo = str2num(tline(64:68));                % Revolution Number at Epoch

    printOut = 1;
    if printOut
        fprintf(fileID,...
            '%6d %12.6f %8.4f %8.4f %8.6f %8.4f %8.4f %8.4f %8.6f %8.4f %8.4f %8.4f %12.4f\n', ...
            objnumber,epoch,incl,raan,e,omega,M,no,a,rNo,BStar);
    end
        
    % check to see if object already exists in satdata
    % if the object doesn't already exist in satdata then add it
    % if it already exists and the new data has a later epoch
    % then replace it, otherwise do nothing
    newdata = 1;
    if count > 0
        for i = 1:count
            if satdata(i).objnumber == objnumber
                newdata = 0;
                % Duplicate data, if epoch is later the overwrite
                if satdata(i).epoch > epoch
                    % Overwrite with updated data
                    satdata(i).epoch = epoch;
                    satdata(i).norad_number = Cnum;
                    satdata(i).objnumber = objnumber;
                    satdata(i).bulletin_number = ID;
                    satdata(i).classification = SC; % almost always 'U'
                    satdata(i).revolution_number = rNo;
                    satdata(i).ephemeris_type = Etype;
                    satdata(i).xmo = M * (pi/180);
                    satdata(i).xnodeo = raan * (pi/180);
                    satdata(i).omegao = omega * (pi/180);
                    satdata(i).xincl = incl * (pi/180);
                    satdata(i).eo = e;
                    satdata(i).apogee = a*(1+e);
                    satdata(i).perigee = a*(1-e);
                    % xno: Period in radians per minute
                    satdata(i).xno = no * TWOPI / MINUTES_PER_DAY;
                    satdata(i).xndt2o = TD1 * 1e-8 * TWOPI / MINUTES_PER_DAY_SQUARED;
                    satdata(i).xndd6o = TD2 * TWOPI / MINUTES_PER_DAY_CUBED;
                    satdata(i).bstar = BStar;
                end
            end
        end
    end
    
    if newdata == 1
        count = count + 1;
        satdata(count).epoch = epoch;
        satdata(count).norad_number = Cnum;
        satdata(count).objnumber = objnumber;
        satdata(count).bulletin_number = ID;
        satdata(count).classification = SC; % almost always 'U'
        satdata(count).revolution_number = rNo;
        satdata(count).ephemeris_type = Etype;
        satdata(count).xmo = M * (pi/180);
        satdata(count).xnodeo = raan * (pi/180);
        satdata(count).omegao = omega * (pi/180);
        satdata(count).xincl = incl * (pi/180);
        satdata(count).eo = e;
        satdata(count).apogee = a*(1+e);
        satdata(count).perigee = a*(1-e);
        satdata(count).xno = no * TWOPI / MINUTES_PER_DAY;
        satdata(count).xndt2o = TD1 * 1e-8 * TWOPI / MINUTES_PER_DAY_SQUARED;
        satdata(count).xndd6o = TD2 * TWOPI / MINUTES_PER_DAY_CUBED;
        satdata(count).bstar = BStar;
    end
end

fclose(fid);
fclose(fileID);

