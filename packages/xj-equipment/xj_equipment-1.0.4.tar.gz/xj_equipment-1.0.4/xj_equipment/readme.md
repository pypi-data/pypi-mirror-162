# 模块介绍

## 1.智能物联系统

1.方案一：采用工厂模式构架，设备基类与设备记录。不通的设备需要连接硬件设备只需要继承扩展即可。初始构架，通用使用通用接口（松规范）。

2.方案二：仅仅提供接口，如果需要接入硬件设备，仅仅需要 开发一个硬件微服务，然后通过接口访问控制类

# SQL

```mysql
CREATE TABLE `equipment_equipment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `equip_code` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '设备唯一编码',
  `region_code` varchar(25) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '行政地区编码',
  `equip_type` tinyint(4) NOT NULL DEFAULT '0' COMMENT '设备类型映射0：未绑定',
  `admin_id` int(11) NOT NULL DEFAULT '0' COMMENT '负责人ID',
  `longitude` varchar(15) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '经度',
  `latitude` varchar(15) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '维度',
  `address` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '详细地址',
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '名称',
  `url` varchar(255) COLLATE utf8_unicode_ci NOT NULL COMMENT '设备路由',
  `mac` varchar(255) COLLATE utf8_unicode_ci NOT NULL COMMENT '设备IP地址',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '设备状态0:正常;1:停止;2:故障；',
  `detail_json` json DEFAULT NULL COMMENT '扩展数据',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_e_code` (`equip_code`) USING BTREE,
  KEY `complex_date_idx` (`created_at`,`updated_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='设备表';


CREATE TABLE `equipment_flag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flag` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '类别名称',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=DYNAMIC;


CREATE TABLE `equipment_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `equip_id` int(11) NOT NULL DEFAULT '0' COMMENT '设备id',
  `flag_id` int(10) NOT NULL DEFAULT '0' COMMENT '状态标签',
  `unit_id` int(10) NOT NULL DEFAULT '0' COMMENT '单位',
  `value` int(10) NOT NULL DEFAULT '0' COMMENT '状态值',
  `status` tinyint(50) NOT NULL COMMENT '状态',
  `summary` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '0' COMMENT '记录摘要',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `e_created` (`equip_id`,`created_at`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='设备日志表';


CREATE TABLE `equipment_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `equip_type` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '设备类型',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=DYNAMIC;


CREATE TABLE `equipment_unit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uint` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '单位',
  `flag_id` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=DYNAMIC;


CREATE TABLE `equipment_use` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `desc` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='设备用途描述';


CREATE TABLE `equipment_use_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `equip_id` int(11) NOT NULL COMMENT '设备表主键ID',
  `use_id` int(11) NOT NULL COMMENT '用途主键ID',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `complex_ue_id` (`equip_id`,`use_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='设备用途映射表';
```



