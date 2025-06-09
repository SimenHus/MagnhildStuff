function [angles,frequencies,velocities, powers] = ReadFile(filepath)
%READFILE Summary of this function goes here
%   Detailed explanation goes here
angles = h5read(filepath, '/angles');
frequencies = h5read(filepath, '/frequencies');
velocities = h5read(filepath, '/velocities');
powers = h5read(filepath, '/powers');
end

