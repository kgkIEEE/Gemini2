%code from https://space.stackexchange.com/questions/19322/converting-orbital-elements-to-cartesian-state-vectors

M_earth = 5.972e+24; % Mass of Earth in kilograms
R_earth = 6378100.0;  % Radius of Earth in meters
G_value = 6.67408e-11;

mu = G_value*M_earth;
Re = R_earth;

% Test vectors
t_test = 0.;
r_test = [2021.32025927e3, 4367.01228542e3, 4767.64403266e3];
v_test = [-4.9999438e3 ,  5.19514042e3, -2.62941783e3];

[a,e,i,omega_AP,omega_LAN,T,h_bar] = cart_2_kep(t_test, r_test, v_test)

[r_vec, v_vec, h_vec] = kep_2_cart(t_test,a,e,i,omega_AP,omega_LAN,T)
r_delta = r_test - r_vec;
v_delta = v_test - v_vec;

[a2,e2,i2,omega_AP2,omega_LAN2,T2,h_bar2] = cart_2_kep(t_test, r_vec, v_vec)
delta_a = a2-a;
delta_e = e2-e;
delta_i = i2-i;
delta_omega_AP = omega_AP2-omega_AP;
delta_omega_LAN = omega_LAN2-omega_LAN;
delta_T = T2-T;

function r = deg2radian(d)
    r = d*pi/180.;
end

function d = radian2deg(r)
    d = r*180/pi;
end

function secs = secondOfYear(dayOfYear)
    secs = 86400.0*dayOfYear;
end

function period = computeOrbitalPeriod(semiMajorAxis)
    M_earth = 5.972e+24; % Mass of Earth in kilograms
    R_earth = 6378100.0;  % Radius of Earth in meters
    G_value = 6.67408e-11;
    mu = G_value*M_earth;
    period = sqrt(4*pi*pi*(power(semiMajorAxis,3))/mu);
end

    
% Keplerian elements
% a - semi-major axis
% e - eccentricity
% i - inclination
% omega_AP - argument of perigee
% omega_LAN - right ascension of the ascending node
% T - time of periapse passage
% EA - eccentric anomaly

% Calculations described at http://ccar.colorado.edu/asen5070/handouts/cart2kep2002.pdf
function [a,e,i,omega_AP,omega_LAN,T,h_bar] = cart_2_kep(t, r_vec,v_vec)
    % Constants
    M_earth = 5.972e+24; % Mass of Earth in kilograms
    R_earth = 6378100.0;  % Radius of Earth in meters
    G_value = 6.67408e-11; % Gravitational constant in m**3/(kg*sec**2)
    mu = G_value*M_earth; % Gravitational force on Earth m**3/sec**2
    %1
    h_bar = cross(r_vec,v_vec);
    h = norm(h_bar);
    %2 Compute radius
    r = norm(r_vec);
    %Compute velocity
    v = norm(v_vec);
    %3 Compute the specific energy, E
    E = (power(v,2)/2) - mu/r;
    %4 Compute semi-major axis, a, in meters
    a = -mu/(2*E);
    %5 Compute eccentricity, e, dimensionless
    e = sqrt(1 - power(h,2)/(a*mu));
    %6 Compute inclination, i
    i = acos(h_bar(3)/h);
    %7 Compute the right ascension of the ascending node, omega_LAN
    omega_LAN = atan2(h_bar(1),-h_bar(2));
    %8 Compute the argument of latitude, lat, in radians
    %beware of division by zero here
    lat = atan2((r_vec(3)/(sin(i))),...
    (r_vec(1)*cos(omega_LAN) + r_vec(2)*sin(omega_LAN)));
    lat2 = atan2(h_bar(1),-h_bar(3));
    % 9 Compute the true anomaly, nu
    % beware of numerical errors here
    % take the real value of cos because Matlab returns 
    % a complex value for -1 or 1
    nu = real(acos((a*(1 - power(e,2)) - r)/(e*r)));
    %10 Compute the argument of periapse, omega_AP
    omega_AP = lat - nu;
    %11 Compute the eccentric anomaly, EA
    EA = 2*atan(sqrt((1-e)/(1+e)) * tan(nu/2));
    %12 Compute the time of periapse passage, T
    period = computeOrbitalPeriod(a);
    T = t - period*(EA - e*sin(EA));
end

% From http://www.jgiesen.de/kepler/kepler.html
% Iterate on a solution of mean anomaly as a function of 
function E = eccAnom (ec, m)
    i = 0;
    maxIter=30;
    delta = 0.00001;
    if (ec < 0.)
        E=m;
    else
        E=pi;
        F = E - ec*sin(m) - m;
    end
    
    while ((abs(F) > delta) && (i<maxIter))
        E = E - F/(1.0-ec*cos(E));
        F = E - ec*sin(E) - m;
        i = i + 1;
        check = E - ec*sin(E);
    end
    
end
    
% Calculations described at http://ccar.colorado.edu/asen5070/handouts/kep2cart_2002.doc               
function [r_vec, v_vec, h_vec] = kep_2_cart(t,a,e,i,omega_AP,omega_LAN,T)
    M_earth = 5.972e+24; % Mass of Earth in kilograms
    R_earth = 6378100.0;  % Radius of Earth in meters
    G_value = 6.67408e-11;
    mu = G_value*M_earth;
    
    %1 Compute the mean anomaly
    %compute orbital period, n
    n = sqrt(mu/power(a,3));
    %mean anomaly, M, is the portion of a period since last periapse
    %
    M = n*(t - T);
    %2 - compute eccentric anomaly, EA
    %solve for Kepler's equation with the Newton-Raphson method
    EA = eccAnom(e, M);
    check = EA - e*sin(EA);
    %3 
    nu = 2*atan(sqrt((1-e)/(1+e)) * tan(EA/2));
    %4
    r = a*(1 - e*cos(EA));
    %5
    h = sqrt(mu*a * (1 - power(e,2)));
    %6
    Om = omega_LAN;
    w =  omega_AP;

    X = r*(cos(Om)*cos(w+nu) - sin(Om)*sin(w+nu)*cos(i));
    Y = r*(sin(Om)*cos(w+nu) + cos(Om)*sin(w+nu)*cos(i));
    Z = r*(sin(i)*sin(w+nu));
    r_vec = [X, Y, Z];

    %7
    p = a*(1-power(e,2));

    V_X = (X*h*e/(r*p))*sin(nu) - (h/r)*(cos(Om)*sin(w+nu) + ...
    sin(Om)*cos(w+nu)*cos(i));
    V_Y = (Y*h*e/(r*p))*sin(nu) - (h/r)*(sin(Om)*sin(w+nu) - ...
    cos(Om)*cos(w+nu)*cos(i));
    V_Z = (Z*h*e/(r*p))*sin(nu) + (h/r)*(cos(w+nu)*sin(i));
    v_vec = [V_X, V_Y, V_Z];

    h_vec = cross(r_vec,v_vec);
end

% This observation should optionally include
% injected signal or noise
function [r_obs, v_obs, h_obs] = observe(r, v, r_offset, v_offset)
        r_obs = [r(1)+r_offset(1), r(2)+r_offset(2), r(3)+r_offset(3)];
        v_obs = [v(1)+v_offset(1), v(2)+v_offset(2), v(3)+v_offset(3)];
        h_obs = cross(r_obs,v_obs);
end