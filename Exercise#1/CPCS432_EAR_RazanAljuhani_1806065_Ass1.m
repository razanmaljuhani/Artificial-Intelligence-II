% Razan Mohammed Aljuhani EAR
% CPCS432 Lab2 
% Lab2 Assignment1

% Read the image
bird_original = imread('bird.jpg');

% Display the original image
subplot(2,2,1);
imshow(bird_original);

% Converts original image to grayscale
bird_gray = rgb2gray(bird_original);

% Display the gray image
subplot(2,2,2);
imshow(bird_gray);

%Save the gray image as jpg.
imwrite(bird_gray,'bird_gray.jpg');

%Generates a mirror image for the gray scale image.
bird_mirror = flipdim(bird_gray,1);

%Display the mirror image
subplot(2,2,3);
imshow(bird_mirror);

% Save the mirror image as jpg.
imwrite(bird_mirror,'bird_mirror.jpg');

% Generates the histogram of the original image  
bird_hist = imhist(bird_original);

% Display the histogram of the original image
subplot(2,2,4);
imhist(bird_original);
