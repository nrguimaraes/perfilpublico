echo "Downloading DataBase "
wget https://drive.inesctec.pt/s/HPDT6orwCiMKaTW/download/PerfilPublicoMongoDB.tar.xz
echo "Download Complete. Unzipping "
tar -xf PerfilPublicoMongoDB.tar.xz
rm PerfilPublicoMongoDB.tar.xz
mv  PerfilPublicoMongoDB db

echo "Downloading Author Images "
wget https://drive.inesctec.pt/s/Bg7CFqSCGeS4stA/download/author_photos.tar.xz
wget https://drive.inesctec.pt/s/Ban8eZ5WZAiGiN9/download/notfound.jpg
wget https://drive.inesctec.pt/s/3rKDESzpJpWq9Tj/download/user.png
echo "Download Complete. Unzipping "
tar -xf author_photos.tar.xz
rm author_photos.tar.xz
mv author_photos app/assets

mv user.png app/assets
mv notfound.jpg app/assets

