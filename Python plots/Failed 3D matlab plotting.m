
% file1 = "common\liggende_hport_hTx_1G-L1.h5ant";
% file2 = "common\standing_hport_vTx_1G-L1.h5ant";
file1 = "common\standing_hport_vTx_1G-L1.h5ant";
file2 = "common\liggende_hport_hTx_1G-L1.h5ant";

[ang1, freq1, vel1, pow1] = ReadFile(file1);
[ang2, freq2, vel2, pow2] = ReadFile(file2);

deg2rad = pi / 180;
n = ceil(length(ang1) / 2);

% Vertical measurement
vertSlice = pow1(end, 1:n);
theta = ang1(1:n);

% Horizontal measurement
horiSlice = pow2(end, :);
phi = ang2;

figure
% polarpattern(theta, vertSlice)
% hold
% polarpattern(ang2, pow2(end, :))

patternFromSlices(vertSlice,theta,horiSlice,phi);