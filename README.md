# Guide to create a valid Ubuntu 24.04 auto-install bootable ISO

The key to a bootable Ubuntu ISO is the partition table and the correct linking of the EFI images.

After much finagling with all online guides, I finally refined an approach that works.

## Inspect original partition table
This work has been validated with a v24.04.3 original ISO.
With one such image, you can run the following command
```shell
$ sgdisk -p /path/to/ubuntu-24.04.3-live-server-amd64.iso
```

The important output is the partition table which needs to  be replicated:

```
Number  Start (sector)    End (sector)  Size       Code  Name
   1              64         6441215   3.1 GiB     0700  ISO9660
   2         6441216         6451375   5.0 MiB     EF00  Appended2
   3         6451376         6451975   300.0 KiB   0700  Gap1
```

## Extract ISO
Now we need to extract the ISO in order to add the autoinstall.yaml to it. For this we can use 7z. If you don't already have it, install it with

```shell
$ sudo apt install -y --no-install-recommends p7zip
```

Once installed, we can make a folder and unpack the ISO

```shell
$ mkdir ubuntu-unpacked
$ 7z x ubuntu-24.04.3-live-server-amd64.iso -oubuntu-unpacked
```

Take notice of the fact there is no space between the -o and the destination folder.

Once that's done, we can copy the autoinstall.yaml into the folder and move into it.

```shell
$ cp autoinstall.yaml ubuntu-unpacked
$ cd ubuntu-unpacked
```

## Enabling auto-install
Now in order for the system to automatically attempt the auto installation, we need to modify the startup configuration.
To do so, we will modify the grub.cfd

```shell
$ vi boot/grub/grub.cfg
```

Find the line that says
```
menuentry "Try or Install Ubuntu Server" {
```

Now two lines below, we need to add the intructions for autoinstall to run, before the triple dashes like so:

```
linux   /casper/vmlinuz  autoinstall ds=nocloud-net;s=file:///cdrom/ ---
```

## Remastering the ISO
Ok now we're ready to rebuild the ISO, which be forewarned, is going to be a lengthy process.

For this we need a complex command, xorriso.
If you don't already have it, go ahead and install it
```shell
$ sudo apt install -y --no-install-recommends xorriso
```

Once in your possession, we can run the actual remaster

```shell
$ xorriso -as mkisofs 
-r -V "Ubuntu-Server 24.04.3 autoinst" 
-J -joliet-long 
-b boot/grub/i386-pc/eltorito.img \
-c boot.catalog \
-no-emul-boot \
-boot-load-size 4 \
-boot-info-table \
-eltorito-alt-boot \
-e "[BOOT]/2-Boot-NoEmul.img" \
-append_partition 2 0xef "[BOOT]/2-Boot-NoEmul.img" \
-appended_part_as_gpt 
-isohybrid-gpt-basdat \
-iso-level 3 
-o /path/to/remastered-image.iso 
.
```

The command as shown is supposed to be run from within the _ubuntu-unpacked_ folder we created earlier.

Once the process terminates, you'll have an ISO.
You can check its properties using sgdisk and file.

```shell
$ file remastered-image.iso
remastered-image.iso: ISO 9660 CD-ROM filesystem data (DOS/MBR boot sector) 'Ubuntu-Server 24.04.3 autoinst' (bootable)
```

```shell
$ sgdisk -p  remastered-image.iso
Disk remastered-image.iso: 6460236 sectors, 3.1 GiB
Sector size (logical): 512 bytes
Disk identifier (GUID): 0B69963F-20E9-4BD9-9832-880DF2E368C7
Partition table holds up to 248 entries
Main partition table begins at sector 2 and ends at sector 63
First usable sector is 64, last usable sector is 6460172
Partitions will be aligned on 4-sector boundaries
Total free space is 1 sectors (512 bytes)

Number  Start (sector)    End (sector)  Size       Code  Name
   1              64         6449411   3.1 GiB     0700  Gap0
   2         6449412         6459571   5.0 MiB     EF00  Appended2
   3         6459572         6460171   300.0 KiB   0700  Gap1
```
