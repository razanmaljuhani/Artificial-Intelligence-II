% Razan Mohammed Aljuhani EAR
% CPCS432 Lab3&4 
% Lab3&4 Assignment2

% 1- Read the image
originalImage = imread("cat.jpg");

%__________________________________Q1________________________________________
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2- Blurring using mean filter
grayImage = rgb2gray(originalImage); % Convert the original image to gray image.
imgd = im2double(grayImage); % Convert the gray image to (black/white) image.
mf = ones(3,3);
mf = mf * 1/9; % Mean filter.
blurredImage = filter2(mf, imgd); % Burring the image by using mean filter.
% Show figures 
figure;
subplot(1,3,1), imshow(originalImage), title (" Original image (Colored). ");
subplot(1,3,2), imshow(imgd), title (" Converted image (black & white). ");
subplot(1,3,3), imshow(blurredImage), title (" Blurred image by using mean filter. ");

%__________________________________Q2________________________________________
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3- Median filtering after adding some noise to it.
% Adding noice to the image
noisedImage = imnoise(originalImage, 'salt & pepper', 0.02); 
% Median filter each channel separately
r = medfilt2(noisedImage(:, :, 1), [3,3]); % Red
g = medfilt2(noisedImage(:, :, 2), [3,3]); % Green
b = medfilt2(noisedImage(:, :, 3), [3,3]); % Blue
% Reconstruct the image from r,g,b channels
medianFilterImage = cat(3, r, g, b); 
% Show figures 
figure;
subplot(1,3,1), image(originalImage), title (" Original image ");
subplot(1,3,2), image(noisedImage), title (" Noised image ");
subplot(1,3,3), image(medianFilterImage), title (" Median filtered image ");

%__________________________________Q3________________________________________
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 4- Horizontal Line detection.
horizontalKernal = [-1,-1,-1; 2,2,2; -1,-1,-1];
horizontalImage = imfilter(originalImage,horizontalKernal);
% Show figures 
figure;
subplot(1,2,1), image(originalImage), title (" Original image ");
subplot(1,2,2), image(horizontalImage), title (" Horizontal Line detected image ");
%__________________________________Q4________________________________________
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%5- Sharpen the image.
sharpFilter = fspecial('unsharp');
sharp = imfilter(originalImage, sharpFilter, 'replicate'); %sharping
sharpMore = imfilter(sharp, sharpFilter, 'replicate'); %Excessive sharping
% Show figures 
figure;
subplot(1,3,1), image(originalImage), title (" Original image ");
subplot(1,3,2),  image(sharp), title (" Sharpened image ");
subplot(1,3,3), image(sharpMore), title (" Excessive sharping attenuates noise image ");
