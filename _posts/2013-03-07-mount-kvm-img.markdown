--
layout: post
Title: "挂载kvm镜像"
Date: 2013-03-07 13:55
comments: true
categories: notes
-- 


kvm的guest镜像可以mount到本地
首先使用qemu-img info  img_file查看镜像使用的文件格式, 通常默认的是raw  

<pre>
[root@ttt data]# qemu-img info vm1.img

image: vm1.img
file format: raw
virtual size: 20G (21474836480 bytes)
disk size: 11G  
</pre>

然后可使用fdisk查看guest使用此镜像时的分区方式:  

<pre>[root@ttt data]# fdisk -ul vm1.img
You must set cylinders.
You can do this from the extra functions menu.

Disk vm1.img: 0 MB, 0 bytes
255 heads, 63 sectors/track, 0 cylinders, total 0 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x0008de38


  Device Boot      Start         End      Blocks   Id  System
vm1.img1            2048     8194047     4096000   82  Linux swap / Solaris
Partition 1 does not end on cylinder boundary.
vm1.img2   *     8194048    41943039    16874496   83  Linux
Partition 2 has different physical/logical endings:
     phys=(1023, 254, 63) logical=(2610, 212, 34)
</pre>



如果是典型的raw方式, 且guest使用的不是lvm的分区管理方式,那方式很简单:
<pre>
losetup /dev/loop0 image.img
kpartx -a /dev/loop0mount /dev/mapper/loop0p1 /mnt/image
</pre>
这样就完成了mount到本地的目的.

以下资料是当img是qcow2或这kvm的guest使用的lvm逻辑卷管理方式时, 如何mount镜像到本地的方法:

<pre>
Mounting a partition from raw image is pretty simple:

losetup /dev/loop0 image.img
kpartx -a /dev/loop0
mount /dev/mapper/loop0p1 /mnt/image
If kernel parameter (as loop in compiled into Fedora’s kernel) like loop.max_part=63 added it is even simplier:
losetup /dev/loop0 image.img
mount /dev/loop0p1 /mnt/image
Alternative way is to specify direct offset to partition:
mount image.img /mnt/image -o loop,offset=32256

To mount qcow2 images there is (at least in F-11 qemu) very useful qemu-nbd util. It shares image through kernel network block device protocol and this allows to mount it:
modprobe nbd max_part=63
qemu-nbd -c /dev/nbd0 image.img
mount /dev/nbd0p1 /mnt/image

If LVM is present on image it could be initialized with:
vgscan
vgchange -ay
mount /dev/VolGroupName/LogVolName /mnt/image

Finishing is done with (depending on how it was initalized):
umount /mnt/image
vgchange -an VolGroupName
killall qemu-nbd
kpartx -d /dev/loop0
losetup -d /dev/loop0


Posted by Alexey Torkhov at 16:33
Labels: Fedora
</pre>
