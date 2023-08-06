### 3.1 User  用户

> 用户模块

**1、User_Base_Info 基础信息表 [NF1]**

R={**id**, <u>user_name</u>, <u>phone</u>, <u>email</u>, full_name, <u>wechat</u>, user_info}

F={<u>user_name</u>->**id**, <u>phone</u>->**id**, <u>email</u>->**id**, <u>wechat</u>->**id**}



**2、User_Auth 安全认证表 [1-1]**

R={**id**, *user_id*, plaintext, password, salt, algorithm, token, ticket, create_time, update_time}
F={*user_id*->**id**}



**3、User_Detail_Info 详细信息表 [1-1]**

R={**id**, *user_id*, nickname, sex, birth, tags, signature, avatar, cover, language, region_code, more}

F={*user_id*->**id**}

more={qq, facebook, vk, weibo, douyin, xiaohongshu, kuaishou} // 更多信息用来存放用户可能填写的扩展内容，由于很多信息不是必填或必须存在的，因此不单独建字段。



**4、*User_Access_Log 访问日志表 [1-N]**

R={**id**, *user_id*, ip, create_time, client_info, more}

F={*user_id*->**id**}



**5、*User_History 操作历史表 [1-N]**

R={**id**, *user_id*, field, old_value, new_value, create_time}

F={*user_id*->**id**}



**6、*User_Restrict_Region 限制范围表**

R={**id**, *user_id*, region_code}

F={ *user_id*->region_code}



**7、*User_Platform 平台表**

R={**id**, platform_name}



**8、*User_Platforms_To_Users - 多对多平台记录表 [N-N]**

R={**id**, *user_id*,  *platform_id*, *platform_user_id*}

F={ *user_id*->*platform_id*, *user_id*->*platform_user_id*, (*platform_id*, *platform_user_id*)->*user_id*}



**9、User_Permission 权限表 [1-N]**

R={**permission_id**, permission_name, }

id={01: VISITOR, 02: STAFF, 03: MANAGER, 04: ADMINISTRATOR, 05: SUPER_ADMINISTRATOR, } // 自定义权限(组)名称，有5个默认值



**10、User_Permission_Value 权限值表 [1-N]**

R={**id**, *permission_id*, value, is_system, is_ban}

value={FINANCE_ONLY_READ} // 权限标识值，一个permission_id可以对应多个value，多值形成一组权限。值为宏名，需要多语言翻译

is_system // 是否系统权限，系统权限不可以删除，默认SUPER_ADMINISTRATOR的所有value都是系统权限。

is_ban={0: NO, 1: YES} // 是否禁用该权限，默认0。使用减法原则，约定无权限值则视为允许。



**11、User_Group 分组表**

R={**id**, *user*_id, group, parent_group, *permission_id*}



**12、User_Contact_Book [NF2]**

R={**id**, *user_id*, phone, phones, telephone, telephones, email, qq, address, more, remark,  }

phones=[phone_1, phone_2, phone_3]

telephone=[telephone_1, telephone_2, telephone_3]

