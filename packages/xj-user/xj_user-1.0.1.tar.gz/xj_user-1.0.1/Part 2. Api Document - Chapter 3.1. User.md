## Chapter 3. Detail Design

> 详细设计

### 3.1. User 用户类

> 用户类



#### 1、用户注册 (user_register)√

- 地址

  ```
  /api/user_register/		POST
  ```

- 参数

  | 参数      | 名词     | 类型   | 必须 | 默认 | 说明                            |
  | --------- | -------- | ------ | ---- | ---- | ------------------------------- |
  | account   | 账号     | string | 是   | -    | 支持用户名、手机、邮箱登录      |
  | password  | 密码     | string | 是   | -    | 仅账号登录时需要                |
  | platform  | 平台名称 | string | 否   | -    | MUZPAY：慕支付平台<br>*后面要改 |
  | full_name | 真实姓名 | string | 是   | -    | -                               |

  

- 返回说明

  | 参数    | 字段名称 | 类型 | 说明 |
  | ------- | -------- | ---- | ---- |
  | user_id | 用户ID   | int  |      |

- 返回

  ```json
  {
      "err": 0,
      "msg": "注册成功",
      "data": {
          "user_id": 280,
          "token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50IjoiMTg3NzgwMDAwNzAifQ.Yl4O_DNLo-dLP775vmstuxF9D-9dClge1oT1Ci3orTQ"
      }
  }
  ```




#### 2、用户登录 (user_login)√

- 地址

  ```
  /api/user_login/		POST
  ```

- 参数

  | 参数     | 名词     | 类型   | 必须 | 默认 | 说明                       |
  | -------- | -------- | ------ | ---- | ---- | -------------------------- |
  | account  | 账号     | string | 是   | -    | 支持用户名、手机、邮箱登录 |
  | password | 密码     | string | 是   | -    | -                          |
  | platform | 平台名称 | string | 是   | -    |                            |

- 返回说明

  | 参数    | 字段名称 | 类型   | 说明 |
  | ------- | -------- | ------ | ---- |
  | user_id | 用户ID   | int    |      |
  | token   | 用户凭证 | string |      |

- 返回

  ```json
  {
      "err": 0,
      "msg": "OK",
      "data": {
          "user_id": 280,
          "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50Ijoic2lleW9vIn0.knmuWtyIKk6zQUOdrKITFPGg9o8Q_uVDQlRDydwtMBA"
      }
  }
  ```


#### 3、用户信息 (user_info)√

- 地址

  ```
  /api/user_info/		GET
  ```

- 参数

  | 参数 | 名词 | 类型 | 必须 | 默认 | 说明 |
  | ---- | ---- | ---- | ---- | ---- | ---- |
  | 无   | -    | -    | -    | -    | -    |

  返回说明

  | 参数      | 字段名称 | 类型   | 说明 |
  | --------- | -------- | ------ | ---- |
  | user_id   | 用户ID   | int    |      |
  | user_name | 用户名   | string |      |
  | full_name | 真实姓名 | string |      |
  | phone     | 手机     | string |      |
  | email     | 邮箱     | string |      |
  | wechat    | 微信号   | string |      |
  | avatar    | 头像URL  | string | todo |
  | user_info | 用户信息 | json   |      |

- 返回

  ```json
  {
      "err": 0,
      "msg": "OK",
      "data": {
          "user_id": 8, 
          "user_name": "sieyoo",
          "full_name": "赵向明",
          "phone": "18778000090",
          "email": "sieyoo@163.com",
          "wechat": "sieyoo",
          "user_info": null
      }
  }
  ```



#### 4、用户编辑 (user_edit)√

- 地址

  ```sh
  /api/user_edit/		POST
  ```

- 参数

  | 参数      | 名词     | 类型   | 必须 | 默认 | 说明 |
  | --------- | -------- | ------ | ---- | ---- | ---- |
  | user_name | 用户名   | string | 否   |      |      |
  | full_name | 真实姓名 | string | 否   |      |      |
  | phone     | 手机     | string | 否   |      |      |
  | email     | 邮箱     | string | 否   |      |      |
  | wechat    | 微信号   | string | 否   |      |      |
  | avatar    | 头像URL  | string | 否   |      |      |
  | user_info | 用户信息 | json   | 否   |      |      |

- 返回说明

  | 参数 | 字段名称 | 类型 | 说明 |
  | ---- | -------- | ---- | ---- |
  | -    | -        | -    | -    |

- 返回

  ```json
  {
      "err": 0,
      "msg": "修改成功",
  }
  ```



#### 5、用户设置密码 (user_password)√

- 地址

  ```sh
  /api/user_password/		POST
  ```

- 参数

  | 参数         | 名词                 | 类型   | 必须 | 默认 | 说明                              |
  | ------------ | -------------------- | ------ | ---- | ---- | --------------------------------- |
  | platform     | 平台                 | string | 是   |      |                                   |
  | account      | 账号                 | string | 是   | -    | -                                 |
  | new_password | 新密码               | string | 是   | -    | -                                 |
  | old_password | 旧密码               | string | -    | -    | old_password和captcha必选二者其一 |
  | captcha      | 验证码，用于忘记密码 | int    | -    | -    | old_password和captcha必选二者其一 |

- 返回说明

  | 参数  | 字段名称 | 类型  | 说明 |
  | ----- | -------- | ----- | ---- |
  | token | 凭证     | token | -    |

- 返回

  ```json
  {
      "err": 0,
      "msg": "修改密码成功",
      "data": {
          "user_id": 280
          "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50Ijoic2lleW9vIn0.knmuWtyIKk6zQUOdrKITFPGg9o8Q_uVDQlRDydwtMBA"
      }
  }
  ```

  

#### 6、用户平台 (user_platform)√

- 地址

  ```
  /api/user_platform/		GET
  ```

- 参数

  | 参数 | 名词 | 类型 | 必须 | 默认 | 说明 |
  | ---- | ---- | ---- | ---- | ---- | ---- |
  | -    | -    | -    | -    | -    | -    |

- 返回说明

  | 参数     | 字段名称 | 类型   | 说明 |
  | -------- | -------- | ------ | ---- |
  | value    | 平台名称 | string |      |
  | platform | 平台名称 | string |      |

- 返回

  ```json
  {
      "err": 0,
      "msg": "OK",
      "data": [
          { 
              "value": "UNKNOWN",
              "platform": "UNKNOWN"
          },
          {
              "value": "MUZPAY",
              "platform": "MUZPAY"
          },
          {
              "value": "LIFE",
              "platform": "LIFE"
          },
          {
              "value": "MUZSTOCK",
              "platform": "MUZSTOCK"
          },
          {
              "value": "PLAN",
              "platform": "PLAN"
          },
          {
              "value": "EHUA",
              "platform": "EHUA"
          },
          {
              "value": "ZHFC",
              "platform": "ZHFC"
          }
      ]
  }
  ```

  

#### 7、用户联系簿 ( user_contact_book )√

- 地址

  ```
  /api/user_contact_book/		GET
  ```

- 参数

  | 参数 | 名词 | 类型 | 必须 | 默认 | 说明 |
  | ---- | ---- | ---- | ---- | ---- | ---- |
  | -    | -    | -    | -    | -    | -    |

- 返回说明

  | 参数      | 字段名称 | 类型   | 说明 |
  | --------- | -------- | ------ | ---- |
  | id        | 用户ID   | int    |      |
  | full_name | 用户     | string |      |

- 返回

  ```
  {
      "err": 0,
      "msg": "OK",
      "data": [
          {
              "id": 3,
              "full_name": "慕支付"
          },
          {
              "id": 270,
              "full_name": "中国移动"
          },
          {
              "id": 276,
              "full_name": "测试002"
          }
      ]
  }
  ```

  
