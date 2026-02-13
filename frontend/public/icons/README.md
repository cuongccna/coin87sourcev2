Thiết kế icon cho Coin87 — phẳng, màu theo ảnh đính kèm (vàng), có chữ logo

Files:
- icon-idea1.svg — chữ `C87` trung tâm, tối giản
- icon-idea2.svg — hình đồng xu với viền, chữ `C87` bên trong
- icon-idea3.svg — chữ `C` cách điệu bằng nét vòng, ô nhỏ chứa `87`

Export PNG (Windows):
- Dùng Inkscape hoặc ImageMagick. Ví dụ:

Inkscape:
```
inkscape icon-idea1.svg --export-filename=icon-idea1-192.png -w 192 -h 192
inkscape icon-idea1.svg --export-filename=icon-idea1-144.png -w 144 -h 144
```

ImageMagick:
```
magick convert -background none -resize 192x192 "icon-idea1.svg" "icon-idea1-192.png"
magick convert -background none -resize 144x144 "icon-idea1.svg" "icon-idea1-144.png"
```

Ghi chú:
- Nếu muốn tôi xuất PNG trực tiếp trong repo, bật sẵn Inkscape/Imagemagick trên máy hoặc cho phép tôi chạy lệnh chuyển đổi.
- Muốn chỉnh lại font, kích thước chữ, bo góc hoặc màu sắc (HEX chính xác), cho tôi biết mã màu hoặc file tham chiếu.