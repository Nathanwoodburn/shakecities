# Template Placeholders

- [Template Placeholders](#template-placeholders)
  - [Colours](#colours)
    - [Background colour (bg\_colour)](#background-colour-bg_colour)
    - [Text colour (text\_colour)](#text-colour-text_colour)
    - [Foreground colour (fg\_colour)](#foreground-colour-fg_colour)
  - [Parts](#parts)
    - [Avatar](#avatar)
    - [HNSChat](#hnschat)
    - [Location](#location)
    - [Email](#email)
    - [Footer (footer)](#footer-footer)
  - [Text Placeholders](#text-placeholders)
    - [Main domain (main\_domain)](#main-domain-main_domain)
    - [Data (data)](#data-data)
  - [Crypto Address Placeholders](#crypto-address-placeholders)
    - [Icons](#icons)
    - [Full parts](#full-parts)
    - [Address only](#address-only)




## Colours
### Background colour (bg_colour)
Use #000000 for the background colour as the app overwrites this colour

### Text colour (text_colour)
Use #1fffff for the background colour as the app overwrites this colour

### Foreground colour (fg_colour)
Use #f1ffff for the background colour as the app overwrites this colour

## Parts
### Avatar
`avatar` can be used to get the avatar of the user.  
If the user doesn't have an avatar this is just 
```html
<h1>domain.shakecities/</h1>
```
If the user does have an avatar this is

```html
<img src='avatar-url' width='200vw' height='200vw' style='border-radius: 50%;margin-right: 5px;'>
```

### HNSChat
If the user has a HNSChat name set this will return
```html
<a href='https://hns.chat/#message:username' target='_blank'>
    <img src='hns_icon' width='20px' height='20px' style='margin-right: 5px;'>
    username/
</a>
```

### Location
If the user has a location set this will return
```html
<img src='location_icon' width='20px' height='30px' style='margin-right: 5px;'>
location
```

### Email
If the user has a email set this will return
```html
<a href='mailto:email@example'>
    <img src='email_icon' width='30px' height='20px' style='margin-right: 5px;margin-left:-10px;'>
    email@example
</a>
```

### Footer (footer)
This is the Shakecities footer. It will always be the same "Powered by Shakecities"


## Text Placeholders
### Main domain (main_domain)
`main_domain` can be used to get the main domain of the site e.g. shakecities.com

### Data (data)
`data` can be used to get the data of the site.  
This is the main body



## Crypto Address Placeholders
### Icons
These are the icons for the crypto addresses.  
There are 2 versions of each icon. One with a contrast to the background colour and one without.

These return the path to the image of the icon (eg. `assets/img/HNS.png`)

They are as follows:
- hns_icon
- hns_icon_invert
- btc_icon
- btc_icon_invert
- eth_icon
- eth_icon_invert

### Full parts
These are the full parts for the crypto addresses.  
They return both the icon and the address.

For example `hns` returns
```html
<img src='hns_icon' width='20px' height='20px' style='margin-right: 5px;'>hs1...
```

The list of full parts are:
- hns
- btc
- eth
- hns_invert
- btc_invert
- eth_invert


### Address only

These are plain text addresses without the icon.  
Eg. `hns_address` returns
```html
hs1...
```

They are as follows:
- hns_address
- btc_address
- eth_address



