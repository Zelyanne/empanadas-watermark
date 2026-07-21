# Empanadas et Régala - Image Watermark Tool

Add your restaurant watermark to any image. The logo is centered as a semi-transparent overlay so people know the photo is from Empanadas et Régala.

## Features

- **Batch processing** – upload up to 50 images at once
- **Centered logo** – your icon is placed in the center of each image
- **Adjustable transparency** – control the watermark opacity
- **Gallery view** – see your watermarked images and save them individually
- **Mobile-friendly** – works well on iPhone / iPad with safari saving

## How It Works

1. Drop your image(s) into the upload area
2. Adjust opacity and logo size using the sliders
3. Click "Watermark images" to process the images
4. Review the watermarked images in the gallery
5. Tap "Save to Photos" on each image to add it to your camera roll

## Development

This project uses:

- **Flask** – backend web framework
- **Pillow** – image processing (PIL)

Create a virtual environment and install dependencies:

```bash
cd sticker
pip3 install -r requirements.txt
```

## Deployment

You can run this locally:

```bash
python3 app.py
```

Or deploy to:
- **[Render.com](https://render.com/)** (free tier)
- **[Railway.app](https://railway.app/)** (free credit)

Make sure `icone.jpeg` (your restaurant logo) is in the project root.

## Screenshots

![Upload interface](screenshot1.png)
![Gallery view](screenshot2.png)