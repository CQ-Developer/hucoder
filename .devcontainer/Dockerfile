FROM archlinux
RUN echo "Server = https://mirrors.tuna.tsinghua.edu.cn/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist \
 && pacman -Syyu --noconfirm \
 && pacman -S --noconfirm --needed git curl zip unzip sudo \
 && groupadd -g 1000 chen \
 && useradd -m -u 1000 -g 1000 -G wheel -s /bin/bash chen \
 && echo "chen:123" | chpasswd \
 && echo "%wheel ALL=(ALL:ALL) ALL" >> /etc/sudoers
WORKDIR /home/chen
USER chen