# 简介
Lebesgue-Utility提供了访问DP-Lebesgue的Python接口和Shell交互工具，可用于上传文件、提交任务、查询任务状态、获取任务结果、停止任务等。


# 下载与安装

Lebesgue-Utility支持Python3，尚未在Python2上进行测试。
当前Lebesgue-Utility提供pip方式安装
```shell
pip3 install git+https://gitee.com/dptech-corp/lebesgue-utility
```
运行方式，在命令行中输入：
```shell
lebesgue
```
首次运行会需要输入账号密码和相关配置。
# 命令行接口
## 查询接口
### Program
查看所有Program的列表
```
$ lebesgue -d
======== Program List ========
Program ID: 940        | Program Name: DPMD       | Balance(yuan): 500.0      | Image Limit: 1    | Storage Limit(GB): 500
Program ID: 842        | Program Name: Hermite    | Balance(yuan): 491.16     | Image Limit: 1    | Storage Limit(GB): 500
```
查看某个Program的具体信息
```
$ lebesgue -d -pgid 940
ID: 101479     | JOB_NAME: test_pytorch         | USER: baixk@dp.tech | JOB_TYPE: indicate   | STATUS: 1   | CREATE_TIME: 2021-10-28 16:29:44 | SPEND_TIME: 2174       | COST:1.51
ID: 101476     | JOB_NAME: HelloLebesgue        | USER: baixk@dp.tech | JOB_TYPE: indicate   | STATUS: 1   | CREATE_TIME: 2021-10-28 16:27:53 | SPEND_TIME: 32         | COST:0.0
ID: 101475     | JOB_NAME: HelloLebesgue        | USER: baixk@dp.tech | JOB_TYPE: indicate   | STATUS: 1   | CREATE_TIME: 2021-10-28 16:27:08 | SPEND_TIME: 32         | COST:0.0
ID: 101425     | JOB_NAME: NewImage2            | USER: baixk@dp.tech | JOB_TYPE: indicate   | STATUS: 4   | CREATE_TIME: 2021-10-27 19:03:36 | SPEND_TIME: 128        | COST:0.0
ID: 101424     | JOB_NAME: NewImage2            | USER: baixk@dp.tech | JOB_TYPE: indicate   | STATUS: 1   | CREATE_TIME: 2021-10-27 19:03:15 | SPEND_TIME: 32         | COST:0.0
ID: 101423     | JOB_NAME: NewImage2            | USER: baixk@dp.tech | JOB_TYPE: indicate   | STATUS: 1   | CREATE_TIME: 2021-10-27 19:00:17 | SPEND_TIME: 32         | COST:0.0
ID: 101392     | JOB_NAME: NewImage             | USER: baixk@dp.tech | JOB_TYPE: indicate   | STATUS: 2   | CREATE_TIME: 2021-10-27 10:26:55 | SPEND_TIME: 64         | COST:0.0
```
### Job Group
查看指定Job Group的信息
```
$ lebesgue -d -jgid 101479
JOB_ID: 117796     | SPEND_TIME: 2174       | STATUS: 2          | RESULT: https://dpcloudserver.oss-cn-shenzhen.aliyuncs.com/dpcloudserver%2Findicate%2F3984567a37c911ecb72900155d38053f%2F3984567a37c911ecb72900155d38053f_download.zip?security-token=xxxxx | INPUT: http://dpcloudserver.oss-cn-shenzhen.aliyuncs.com/dpcloudserver/indicate/test.zip | COST:1.51  | CREATE_TIME:2021-10-28 16:29:44 | UPDATE_TIME:2021-10-28 17:08:08
```
### Job
查看指定Job的信息
```
$ lebesgue -d -jid 117796
JOB_ID:        117796
JOB_GROUP_ID:  101479
STATUS:        2
SPEND_TIME:    2174
COST:          151.0
CREATE_TIME:   2021-10-28 16:29:44
UPATE_TIME:    2021-10-28 17:08:08
INPUT:         http://dpcloudserver.oss-cn-shenzhen.aliyuncs.com/dpcloudserver/indicate/test.zip
RESULT:        https://dpcloudserver.oss-cn-shenzhen.aliyuncs.com/dpcloudserver%2Findicate%test.zip
```
### 机型
查看所有可选机型及报价的列表
```
$ lebesgue -m
如果您使用的terminal无法上下滚动，可以使用下列命令，并通过快捷键 i j 进行逐行滚动，或用上下箭头，PgUp PgDn，按 q 键退出。
$ lebesgue -m | less
======== Machine Type List ========
INSTANCE_TYPE: c32_m64_cpu               | CPU_CORE: 32   | GPU: cpu              | MEM(GB): 64   | PLATFORM: sugon | SPOT_PRICE(yuan/h): 1.92  | ON_DEMAND_PRICE(yuan/h): 1.92
INSTANCE_TYPE: c16_m32_cpu               | CPU_CORE: 16   | GPU: cpu              | MEM(GB): 32   | PLATFORM: sugon | SPOT_PRICE(yuan/h): 0.96  | ON_DEMAND_PRICE(yuan/h): 0.96
INSTANCE_TYPE: c8_m16_cpu                | CPU_CORE: 8    | GPU: cpu              | MEM(GB): 16   | PLATFORM: sugon | SPOT_PRICE(yuan/h): 0.48  | ON_DEMAND_PRICE(yuan/h): 0.48
INSTANCE_TYPE: c4_m8_cpu                 | CPU_CORE: 4    | GPU: cpu              | MEM(GB): 8    | PLATFORM: sugon | SPOT_PRICE(yuan/h): 0.24  | ON_DEMAND_PRICE(yuan/h): 0.24
INSTANCE_TYPE: c2_m4_cpu                 | CPU_CORE: 2    | GPU: cpu              | MEM(GB): 4    | PLATFORM: sugon | SPOT_PRICE(yuan/h): 0.12  | ON_DEMAND_PRICE(yuan/h): 0.12
INSTANCE_TYPE: c32_m64_dcu*4             | CPU_CORE: 32   | GPU: dcu*4            | MEM(GB): 64   | PLATFORM: sugon | SPOT_PRICE(yuan/h): 4.8   | ON_DEMAND_PRICE(yuan/h): 4.8
INSTANCE_TYPE: c24_m48_dcu*3             | CPU_CORE: 24   | GPU: dcu*3            | MEM(GB): 48   | PLATFORM: sugon | SPOT_PRICE(yuan/h): 3.6   | ON_DEMAND_PRICE(yuan/h): 3.6
INSTANCE_TYPE: c16_m32_dcu*2             | CPU_CORE: 16   | GPU: dcu*2            | MEM(GB): 32   | PLATFORM: sugon | SPOT_PRICE(yuan/h): 2.4   | ON_DEMAND_PRICE(yuan/h): 2.4
INSTANCE_TYPE: c8_m16_dcu*1              | CPU_CORE: 8    | GPU: dcu*1            | MEM(GB): 16   | PLATFORM: sugon | SPOT_PRICE(yuan/h): 1.2   | ON_DEMAND_PRICE(yuan/h): 1.2
INSTANCE_TYPE: c96_m768_cpu              | CPU_CORE: 96   | GPU: cpu              | MEM(GB): 768  | PLATFORM: ali | SPOT_PRICE(yuan/h): 6.72  | ON_DEMAND_PRICE(yuan/h): 20.16
INSTANCE_TYPE: c96_m768_8 * NVIDIA V100  | CPU_CORE: 96   | GPU: 8 * NVIDIA V100  | MEM(GB): 768  | PLATFORM: ali | SPOT_PRICE(yuan/h): 36.0  | ON_DEMAND_PRICE(yuan/h): 144.0
INSTANCE_TYPE: c96_m736_8 * NVIDIA V100  | CPU_CORE: 96   | GPU: 8 * NVIDIA V100  | MEM(GB): 736  | PLATFORM: ali | SPOT_PRICE(yuan/h): 36.0  | ON_DEMAND_PRICE(yuan/h): 144.0
INSTANCE_TYPE: c96_m384_cpu              | CPU_CORE: 96   | GPU: cpu              | MEM(GB): 384  | PLATFORM: ali | SPOT_PRICE(yuan/h): 6.24  | ON_DEMAND_PRICE(yuan/h): 18.72
INSTANCE_TYPE: c96_m384_8 * NVIDIA V100  | CPU_CORE: 96   | GPU: 8 * NVIDIA V100  | MEM(GB): 384  | PLATFORM: ali | SPOT_PRICE(yuan/h): 36.0  | ON_DEMAND_PRICE(yuan/h): 144.0
INSTANCE_TYPE: c96_m384_8 * NVIDIA GPU B | CPU_CORE: 96   | GPU: 8 * NVIDIA GPU B | MEM(GB): 384  | PLATFORM: ali | SPOT_PRICE(yuan/h): 32.0  | ON_DEMAND_PRICE(yuan/h): 128.0
INSTANCE_TYPE: c96_m384_4 * NVIDIA T4    | CPU_CORE: 96   | GPU: 4 * NVIDIA T4    | MEM(GB): 384  | PLATFORM: ali | SPOT_PRICE(yuan/h): 10.0  | ON_DEMAND_PRICE(yuan/h): 40.0
```
### 镜像
查看指定Program下的所有可选镜像列表
```
$ lebesgue -im -pgid 940
======== Image List ========
Program Name: DPMD       | ID: 1     | Image Name: lebesgue-base-img              | Status: 2    | Platform: ali | Disk Size(GB): None  | Comment: None
Program Name: DPMD       | ID: 77    | Image Name: Lebesgue-dpgen-01              | Status: 2    | Platform: ali | Disk Size(GB): 40    | Comment: None
Program Name: DPMD       | ID: 108   | Image Name: Lebesgue-dpgen-01.1-img        | Status: 2    | Platform: ali | Disk Size(GB): 40    | Comment: None
Program Name: DPMD       | ID: 134   | Image Name: lebesgue-base-img-01           | Status: 2    | Platform: ali | Disk Size(GB): 40    | Comment: None
Program Name: DPMD       | ID: 145   | Image Name: lebesgue-vasp-user             | Status: 2    | Platform: ali | Disk Size(GB): 40    | Comment: None
Program Name: DPMD       | ID: 220   | Image Name: lebesgue-base-img-02           | Status: 2    | Platform: ali | Disk Size(GB): 40    | Comment: lebesgue-base-img-02
Program Name: DPMD       | ID: 247   | Image Name: Lebesgue-dpgen-02-img          | Status: 2    | Platform: ali | Disk Size(GB): 40    | Comment: None
Program Name: DPMD       | ID: 254   | Image Name: deepmd-kit:1.3.3               | Status: 2    | Platform: ali | Disk Size(GB): 100   | Comment: None
Program Name: DPMD       | ID: 263   | Image Name: vasp:5.4.4                     | Status: 2    | Platform: ali | Disk Size(GB): None  | Comment: None
Program Name: DPMD       | ID: 264   | Image Name: deepmd-kit:2.0.2               | Status: 2    | Platform: ali | Disk Size(GB): None  | Comment: None
Program Name: DPMD       | ID: 268   | Image Name: gromacs-dp:2020.2              | Status: 2    | Platform: ali | Disk Size(GB): 50    | Comment: None
Program Name: DPMD       | ID: 270   | Image Name: deepmd-kit:2.0.1               | Status: 2    | Platform: ali | Disk Size(GB): None  | Comment: None
```
### 总体任务情况
## 提交接口
-i 指定任务的配置文件
-p 指定输入文件的目录
Lebesgue会将指定目录打包上传，在服务器上解压后，将工作目录切换为该目录。

下列镜像为当前适配了Lebesgue 2.0接口的镜像，其他镜像会很快迁移到2.0，如果不确定请随时咨询：
deepmd-kit:2.0.2
vasp:5.4.4
deepmd-kit:2.0.1

配置文件示例： ./params/indicate.json
```
{
    "job_name": "HelloLebesgue",
    "command": " sh ./work.sh > tmp_log 2>&1 ",
    # 工作目录为输入文件的目录
    "log_file": "tmp_log",
    # log_file为在任务结束前即可随时查询的日志文件
    "backward_files": ["tmp_log"],
    # backward_files为需要打包上传的文件列表，置空则为当前工作目录内的所有文件
    "program_id": 940,
    "platform": "ali",
    "job_group_id": "",
    # 如果不指定job_group_id，则每次都会创建新的job_group，否则会将该任务追加到指定的job_group下
    "disk_size": 500,
    # disk_size为额外的数据盘大小，单位为GB，系统盘不需要指定大小，默认和镜像大小相同
    "machine_type": "c2_m2_cpu",
    # machine_type为固定机型
    "image_name": "deepmd-kit:2.0.2"
    # image_name为镜像名称
}

```
提交任务示例：
```
$ lebesgue -i ./params/indicate.json -p ./input
Zip File Success!: /home/unboundwill/src/lebesgue-sdk/input.zip
Uploading
Uploading: 0.0%
Uploaded
Insert job succeed. JOB GROUP ID: 101425, JOB ID: 117320
```

## 下载接口
### 指定JOB GROUP
将指定 job_group_id 中的所有JOB的结果数据进行下载
该命令会在config.json中指定的"result"字段指定的目录中创建目录 <job_group_id>/
并将每个JOB的结果数据下载到该目录中的 <job_id>.zip
然后解压缩到 <job_id>/ 目录下
```
$ lebesgue -D -jgid 101425
成功下载到 /home/unboundwill/src/lebesgue-sdk/result/101425/
```
### 指定JOB
将指定 job_id 的结果数据进行下载
该命令会在config.json中指定的"result"字段指定的目录中创建目录 <job_group_id>/
并将指定的JOB的结果数据下载到该目录中的 <job_id>.zip
然后解压缩到 <job_id>/ 目录下
```
$ lebesgue -D -jid 117313
Downloaded to /home/unboundwill/src/lebesgue-sdk/result/101425/117313/
```
## 停止接口
停止任务，将该任务状态设置为失败。
```
$ lebesgue -k -jid 117313
$ lebesgue --kill -jid 117313
```
## 完成任务接口
提前完成任务或任务组，将该任务状态设置为已完成。
```
$ lebesgue -t -jid 117313
$ lebesgue -t -jgid 101055
$ lebesgue --terminate -jid 117313
$ lebesgue --terminate -jgid 101055
```
## 删除接口
删除指定的Job Group
```
$ lebesgue --delete -jgid 101055
```
