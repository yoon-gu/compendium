# Introduction
이 문서는 기술 지원 에이전트를 위한 종합 안내서입니다. 휴대전화의 cellular service, mobile data connectivity, Multimedia Messaging Service (MMS)에서 흔한 문제를 겪는 사용자를 지원하기 위한 상세 절차와 문제 해결 단계를 제공합니다. 이 매뉴얼은 이러한 서비스가 작동하는 방식, 흔한 문제, 해결에 사용할 수 있는 도구를 개괄하여 에이전트가 문제를 효율적으로 진단하고 해결하도록 돕는 구조로 되어 있습니다.

다루는 주요 절은 다음과 같습니다:
*   **Understanding and Troubleshooting Your Phone's Cellular Service**: network connection, signal strength, SIM card 문제와 관련된 이슈를 다룹니다.
*   **Understanding and Troubleshooting Your Phone's Mobile Data**: speed와 connectivity를 포함하여 cellular network를 통한 internet access 문제에 초점을 맞춥니다.
*   **Understanding and Troubleshooting MMS (Picture/Video Messaging)**: multimedia messages의 송수신과 관련된 문제를 다룹니다.

인간 에이전트에게 전송하기 전에 사용자의 문제를 해결할 수 있는 모든 가능한 방법을 시도해야 합니다.

# What the user can do on their device
다음은 사용자가 자신의 기기에서 수행할 수 있는 행동입니다.
기술 지원의 일부로 고객이 일련의 행동을 수행하도록 도와야 하므로, 이를 잘 이해해야 합니다.

## Diagnostic Actions (Read-only)
1. **check_status_bar** - 휴대전화의 status bar(화면 상단 영역)에 현재 표시되는 아이콘을 보여 줍니다.
   - Airplane mode status (활성화되면 "Airplane Mode")
   - Network signal strength ("No Signal", "Poor", "Fair", "Good", "Excellent")
   - Network technology (예: "5G", "4G" 등)
   - Mobile data status ("Data Enabled" 또는 "Data Disabled")
   - Data saver status (활성화되면 "Data Saver")
   - Wi-Fi status ("Connected to [SSID]" 또는 "Enabled")
   - VPN status (연결되면 "VPN Connected")
   - Battery level ("[percentage]%")
2. **check_network_status** - cellular networks와 Wi-Fi에 대한 휴대전화의 connection status를 확인합니다. airplane mode status, signal strength, network type, mobile data 활성화 여부, data roaming 활성화 여부를 보여 줍니다. Signal strength는 "none", "poor" (1bar), "fair" (2 bars), "good" (3 bars), "excellent" (4+ bars)일 수 있습니다.
3. **check_network_mode_preference** - 휴대전화의 network mode preference를 확인합니다. 휴대전화가 연결하기를 선호하는 cellular network 유형(예: 5G, 4G, 3G, 2G)을 보여 줍니다.
4. **check_sim_status** - SIM card가 올바르게 작동하는지 확인하고 현재 status를 표시합니다. SIM이 active인지, missing인지, PIN 또는 PUK code로 locked되었는지 보여 줍니다.
5. **check_data_restriction_status** - 휴대전화에 활성화된 data-limiting features가 있는지 확인합니다. Data Saver mode가 켜져 있는지와 background data usage가 전역적으로 제한되는지 보여 줍니다.
6. **check_apn_settings** - 휴대전화가 carrier의 mobile data network에 연결하는 데 사용하는 technical APN settings를 확인합니다. picture messaging을 위한 현재 APN name과 MMSC URL을 보여 줍니다.
7. **check_wifi_status** - Wi-Fi connection status를 확인합니다. Wi-Fi가 켜져 있는지, 어떤 network에 연결되어 있는지(있는 경우), signal strength를 보여 줍니다.
8. **check_wifi_calling_status** - 기기에서 Wi-Fi Calling이 활성화되어 있는지 확인합니다. 이 기능은 cellular network 대신 Wi-Fi network를 통해 전화를 걸고 받을 수 있게 합니다.
9. **check_vpn_status** - VPN (Virtual Private Network) connection을 사용 중인지 확인합니다. VPN이 active인지, connected인지 보여 주고 사용 가능한 connection details를 표시합니다.
10. **check_installed_apps** - 휴대전화에 설치된 모든 apps의 이름을 반환합니다.
11. **check_app_status** - 특정 app에 대한 상세 정보를 확인합니다. 해당 app의 permissions와 background data usage settings를 보여 줍니다.
12. **check_app_permissions** - 특정 app이 현재 어떤 permissions를 갖고 있는지 확인합니다. app이 storage, camera, location 등의 기능에 접근 권한이 있는지 보여 줍니다.
13. **run_speed_test** - 현재 internet connection speed(download speed)를 측정합니다. connection quality와 지원 가능한 activities에 대한 정보를 제공합니다. Download speed는 "unknown", "very poor", "poor", "fair", "good", "excellent"일 수 있습니다.
14. **can_send_mms** - messaging app이 MMS messages를 보낼 수 있는지 확인합니다.

## Fix Actions (Write/Modify)
1. **set_network_mode_preference** - 휴대전화가 연결하기를 선호하는 cellular network 유형(예: 5G, 4G, 3G)을 변경합니다. 더 빠른 networks(5G, 4G)는 더 빠른 data를 제공하지만 battery를 더 많이 사용할 수 있습니다.
2. **toggle_airplane_mode** - Airplane Mode를 ON 또는 OFF로 전환합니다. ON이면 cellular, Wi-Fi, Bluetooth를 포함한 모든 wireless communications가 끊어집니다.
3. **reseat_sim_card** - SIM card를 제거하고 다시 삽입하는 것을 시뮬레이션합니다. recognition issues 해결에 도움이 될 수 있습니다.
4. **toggle_data** - 휴대전화의 mobile data connection을 ON 또는 OFF로 전환합니다. Wi-Fi를 사용할 수 없을 때 휴대전화가 internet access를 위해 cellular data를 사용할 수 있는지 제어합니다.
5. **toggle_roaming** - Data Roaming을 ON 또는 OFF로 전환합니다. ON이면 roaming이 enabled되고 휴대전화가 carrier coverage 밖의 지역에서 data networks를 사용할 수 있습니다.
6. **toggle_data_saver_mode** - Data Saver mode를 ON 또는 OFF로 전환합니다. ON이면 data usage를 줄이며, data speed에 영향을 줄 수 있습니다.
7. **set_apn_settings** - 휴대전화의 APN settings를 설정합니다.
8. **reset_apn_settings** - APN settings를 default settings로 재설정합니다.
9. **toggle_wifi** - 휴대전화의 Wi-Fi radio를 ON 또는 OFF로 전환합니다. 휴대전화가 internet access를 위해 wireless networks를 발견하고 연결할 수 있는지 제어합니다.
10. **toggle_wifi_calling** - Wi-Fi Calling을 ON 또는 OFF로 전환합니다. 이 기능은 cellular network 대신 Wi-Fi를 통해 전화를 걸고 받을 수 있게 하며, cellular signal이 약한 지역에서 도움이 될 수 있습니다.
11. **connect_vpn** - VPN (Virtual Private Network)에 연결합니다.
12. **disconnect_vpn** - active VPN (Virtual Private Network) connection을 끊습니다. internet traffic을 VPN server를 통해 라우팅하는 것을 중지하며, connection speed나 content access에 영향을 줄 수 있습니다.
13. **grant_app_permission** - 특정 permission(예: storage, camera, location 접근)을 app에 부여합니다. 일부 app functions가 제대로 작동하는 데 필요합니다.
14. **reboot_device** - 휴대전화를 완전히 다시 시작합니다. 실행 중인 모든 services와 connections를 새로 고쳐 많은 temporary software glitches를 해결하는 데 도움이 될 수 있습니다.

# Understanding and Troubleshooting Your Phone's Cellular Service
이 절은 사용자의 휴대전화가 cellular network(흔히 "service"라고 함)에 연결되는 방식과 흔한 문제를 해결하기 위한 절차를 에이전트에게 자세히 설명합니다. calls, texts, mobile data에는 양호한 cellular service가 필요합니다.

## Common Service Issues and Their Causes
사용자가 service problems를 겪고 있다면, 흔한 원인은 다음과 같습니다:

*   **Airplane Mode is ON**: cellular를 포함한 모든 wireless radios를 비활성화합니다.
*   **SIM Card Problems**:
    *   삽입되지 않았거나 제대로 장착되지 않았습니다.
    *   잘못된 PIN/PUK entries로 인해 locked되었습니다.
*   **Incorrect Network Settings**: APN settings가 잘못되어 service loss가 발생할 수 있습니다.
*   **Carrier Issues**: billing problems로 인해 회선이 inactive일 수 있습니다.


## Diagnosing Service Issues
`check_status_bar()`를 사용해 사용자가 service issue를 겪고 있는지 확인할 수 있습니다.
cellular service가 있으면, status bar는 signal strength indicator를 반환합니다.

## Troubleshooting Service Problems
### Airplane Mode
Airplane Mode는 cellular를 포함한 모든 wireless radios를 비활성화하는 기능입니다. 활성화되어 있으면 모든 cellular connection을 막습니다.
`check_status_bar()` 또는 `check_network_status()`를 사용해 Airplane Mode가 ON인지 확인할 수 있습니다.
ON이면, 사용자에게 `toggle_airplane_mode()`를 사용해 OFF로 전환하도록 안내하세요.

### SIM Card Issues
SIM card는 사용자의 정보를 담고 휴대전화가 cellular network에 연결되도록 하는 물리적 카드입니다.
SIM card 문제는 service의 완전한 손실로 이어질 수 있습니다.
가장 흔한 문제는 SIM card가 제대로 장착되지 않았거나 사용자가 잘못된 PIN 또는 PUK code를 입력한 것입니다.
`check_sim_status()`를 사용해 SIM card의 status를 확인하세요.
"Missing"으로 표시되면, 사용자에게 `reseat_sim_card()`를 사용해 SIM card가 올바르게 삽입되도록 안내하세요.
"Locked"로 표시되면(잘못된 PIN 또는 PUK entries로 인한 경우), **SIM security 지원을 위해 technical support로 에스컬레이션하세요**.
"Active"로 표시되면, SIM 자체는 정상일 가능성이 높습니다.

### Incorrect APN Settings
Access Point Name (APN) settings는 network connectivity에 매우 중요합니다.
`check_apn_settings()`가 "Incorrect"를 표시하면, 사용자에게 `reset_apn_settings()`를 사용해 APN settings를 재설정하도록 안내하세요.
APN settings를 재설정한 후에는 변경 사항을 적용하기 위해 사용자에게 `reboot_device()`를 사용하도록 지시해야 합니다.

### Line Suspension
회선이 suspended되어 있으면, 사용자는 cellular service를 사용할 수 없습니다.
회선이 suspended되어 있는지 조사하세요. line suspensions 처리 지침은 general agent policy를 참조하세요.
*   회선이 suspended되어 있고 에이전트가 suspension을 해제할 수 있다면(general policy에 따라), service가 복구되었는지 확인하세요.
*   suspension을 에이전트가 해제할 수 없다면(예: general policy에 언급된 contract end date 또는 에이전트가 해결할 수 없는 다른 이유로 인해), **technical support로 에스컬레이션하세요**.


# Understanding and Troubleshooting Your Phone's Mobile Data
이 절은 Wi-Fi를 사용할 수 없을 때 사용자의 휴대전화가 internet access를 위해 mobile data를 사용하는 방식과 흔한 connectivity 및 speed issues의 문제 해결을 에이전트에게 설명합니다.

## What is Mobile Data?
Mobile data는 carrier의 cellular network를 사용해 휴대전화가 internet에 연결되도록 합니다. 이를 통해 Wi-Fi에 연결되어 있지 않을 때 websites browsing, apps 사용, video streaming, emails 송수신이 가능합니다. status bar는 보통 active mobile data connection과 그 유형을 나타내기 위해 "5G", "LTE", "4G", "3G", "H+", "E" 같은 icons를 표시합니다.

## Prerequisites for Mobile Data
mobile data가 작동하려면 사용자는 먼저 **cellular service**를 보유해야 합니다. 사용자가 service를 보유하지 않았다면 "Understanding and Troubleshooting Your Phone's Cellular Service" 가이드를 참조하세요.

## Common Mobile Data Issues and Causes
cellular service가 있어도 mobile data problems가 발생할 수 있습니다. 흔한 이유는 다음과 같습니다:

*   **Airplane Mode is ON**: mobile data를 포함한 모든 wireless connections를 비활성화합니다.
*   **Mobile Data is Turned OFF**: phone settings에서 mobile data의 main switch가 비활성화되어 있을 수 있습니다.
*   **Roaming Issues (When User is Abroad)**:
    *   phone에서 Data Roaming이 turned OFF되어 있습니다.
    *   회선에 roaming이 enabled되어 있지 않습니다.
*   **Data Plan Limits Reached**: 사용자가 monthly data allowance를 모두 사용했으며, carrier가 data를 느리게 하거나 차단했을 수 있습니다.
*   **Data Saver Mode is ON**: 이 기능은 background data usage를 제한하며, data를 절약하기 위해 일부 apps 또는 services가 느리거나 응답하지 않는 것처럼 보이게 할 수 있습니다.
*   **VPN Issues**: active VPN connection이 느리거나 잘못 구성되어 data speeds 또는 connectivity에 영향을 줄 수 있습니다.
*   **Bad Network Preferences**: 휴대전화가 2G/3G 같은 older network technology로 설정되어 있습니다.

## Diagnosing Mobile Data Issues
`run_speed_test()`를 사용해 mobile data의 잠재적 문제를 확인할 수 있습니다.
mobile data를 사용할 수 없으면 speed test는 'no connection'을 반환해야 합니다.
data를 사용할 수 있으면 speed test는 data speed도 반환합니다.
'Excellent'보다 낮은 모든 speed는 느린 것으로 간주됩니다.

## Troubleshooting Mobile Data Problems
### Airplane Mode
Airplane Mode를 확인하고 끄는 방법에 대한 지침은 "Understanding and Troubleshooting Your Phone's Cellular Service" 절을 참조하세요.

### Mobile Data Disabled
Mobile data switch는 carrier의 cellular network를 사용해 휴대전화가 internet에 연결되도록 합니다.
`check_network_status()`가 mobile data가 disabled라고 표시하면, 사용자에게 `toggle_data()`를 사용해 mobile data를 ON으로 전환하도록 안내하세요.

### Addressing Data Roaming Problems
Data roaming은 사용자가 home network 밖의 지역(예: 해외 여행 중)에서 휴대전화의 data connection을 사용할 수 있게 합니다.
사용자가 carrier의 primary coverage area 밖(roaming)에 있고 mobile data가 작동하지 않으면, `toggle_roaming()`을 사용해 Data Roaming이 ON인지 확인하도록 안내하세요.
사용자가 제공한 전화번호와 연결된 회선에 roaming이 enabled되어 있는지 확인해야 합니다. 그렇지 않으면 사용자는 home network 밖의 지역에서 휴대전화의 data connection을 사용할 수 없습니다.
roaming 활성화에 대한 지침은 general policy를 참조하세요.

### Data Saver Mode
Data Saver mode는 background data usage를 제한하고 data speeds에 영향을 줄 수 있는 기능입니다.
`check_data_restriction_status()`가 "Data Saver mode is ON"을 표시하면, 사용자에게 `toggle_data_saver_mode()`를 사용해 OFF로 전환하도록 안내하세요.

### VPN Connection Issues
VPN (Virtual Private Network)은 internet traffic을 암호화하고 data speeds와 security 개선에 도움이 될 수 있는 기능입니다.
그러나 어떤 경우에는 VPN이 speed를 크게 떨어뜨릴 수 있습니다.
`check_vpn_status()`가 "VPN is ON and connected"이고 performance level이 "Poor"라고 표시하면, 사용자에게 `disconnect_vpn()`을 사용해 VPN 연결을 끊도록 안내하세요.

### Data Plan Limits Reached
각 plan은 월별 maxium data usage를 명시합니다.
사용자가 제공한 전화번호와 연결된 회선의 data usage가 plan의 data limit를 초과하면, data connectivity가 끊깁니다.
사용자에게는 2가지 options가 있습니다:
- 더 많은 data가 포함된 plan으로 변경합니다.
- plan에 명시된 GB당 가격으로 data를 "refueling"하여 회선에 더 많은 data를 추가합니다.
이 options에 대한 지침은 general policy를 참조하세요.

### Optimizing Network Mode Preferences
Network mode preferences는 휴대전화가 연결할 cellular network 유형을 결정하는 settings입니다.
2G/3G 같은 older modes를 사용하면 speed가 크게 제한될 수 있습니다.
`check_network_mode_preference()`가 "2G" 또는 "3G"를 표시하면, 사용자에게 `set_network_mode_preference(mode: str)`를 mode `"4g_5g_preferred"`와 함께 사용해 휴대전화가 5G에 연결되도록 안내하세요.

# Understanding and Troubleshooting MMS (Picture/Video Messaging)
이 절은 사진, 동영상 또는 오디오가 포함된 messages를 보내고 받을 수 있게 하는 Multimedia Messaging Service (MMS)를 문제 해결하는 방법을 에이전트에게 설명합니다.

## What is MMS?
MMS는 multimedia content를 허용하는 SMS (text messaging)의 확장입니다. 사용자가 messaging app을 통해 친구에게 photo를 보낼 때, 일반적으로 MMS를 사용합니다.

## Prerequisites for MMS
MMS가 작동하려면 사용자는 cellular service와 mobile data(어떤 speed든)를 보유해야 합니다.
자세한 내용은 "Understanding and Troubleshooting Your Phone's Cellular Service" 및 "Understanding and Troubleshooting Your Phone's Mobile Data" 절을 참조하세요.

## Common MMS Issues and Causes
*   **No Cellular Service or Mobile Data Off/Not Working**: 가장 흔한 이유입니다. MMS는 이들에 의존합니다.
*   **Incorrect APN Settings**: 특히 MMSC URL이 누락되었거나 잘못되었습니다.
*   **Connected to 2G Network**: 2G networks는 일반적으로 MMS에 적합하지 않습니다.
*   **Wi-Fi Calling Configuration**: 어떤 경우에는 Wi-Fi Calling이 구성된 방식이 MMS에 영향을 줄 수 있으며, 특히 carrier가 Wi-Fi를 통한 MMS를 지원하지 않는 경우 그렇습니다.
*   **App Permissions**: messaging app은 storage(media files용)와 보통 SMS functionalities에 접근할 permission이 필요합니다.

## Diagnosing MMS Issues
사용자의 휴대전화에서 `can_send_mms()` 도구를 사용해 사용자가 MMS issue를 겪고 있는지 확인할 수 있습니다.

## Troubleshooting MMS Problems
### Ensuring Basic Connectivity for MMS
성공적인 MMS messaging은 기본적인 service와 data connectivity에 의존합니다. 이 절은 이러한 prerequisites를 확인하는 내용을 다룹니다.
먼저 사용자가 calls를 할 수 있고 mobile data가 다른 apps(예: web browsing)에 대해 작동하는지 확인하세요. 필요하면 "Understanding and Troubleshooting Your Phone's Cellular Service" 및 "Understanding and Troubleshooting Your Phone's Mobile Data" 절을 참조하세요.

### Unsuitable Network Technology for MMS
MMS에는 특정 network requirements가 있으며, 2G 같은 older technologies는 충분하지 않습니다. 이 절은 network type을 확인하고 필요한 경우 변경하는 방법을 설명합니다.
MMS에는 최소 3G network connection이 필요하며, 2G networks는 일반적으로 적합하지 않습니다.
`check_network_status()`가 "2G"를 표시하면, 사용자에게 `set_network_mode_preference(mode: str)`를 사용해 3G, 4G 또는 5G를 포함하는 network mode(예: `"4g_5g_preferred"` 또는 `"4g_only"`)로 전환하도록 안내하세요.

### Verifying APN (MMSC URL) for MMS
MMSC는 Multimedia Messaging Service Center입니다. MMS messages를 처리하는 server입니다. 올바른 MMSC URL이 없으면 사용자는 MMS messages를 보내거나 받을 수 없습니다.
이는 APN settings의 일부로 지정됩니다. 잘못된 MMSC URL은 MMS issues의 매우 흔한 원인입니다.
`check_apn_settings()`가 MMSC URL이 설정되어 있지 않다고 표시하면, 사용자에게 `reset_apn_settings()`를 사용해 APN settings를 재설정하도록 안내하세요.
APN settings를 재설정한 후에는 변경 사항을 적용하기 위해 사용자에게 `reboot_device()`를 사용하도록 지시해야 합니다.

### Investigating Wi-Fi Calling Interference with MMS
Wi-Fi Calling settings는 때때로 MMS functionality와 충돌할 수 있습니다.
`check_wifi_calling_status()`가 "Wi-Fi Calling is ON"을 표시하면, 사용자에게 `toggle_wifi_calling()`을 사용해 OFF로 전환하도록 안내하세요.

### Messaging App Lacks Necessary Permissions
messaging app은 media를 처리하고 messages를 보내기 위해 specific permissions가 필요합니다.
`check_app_permissions(app_name="messaging")`가 "storage" 및 "sms" permissions가 granted로 나열되어 있지 않다고 표시하면, 사용자에게 `grant_app_permission(app_name="messaging", permission="storage")` 및 `grant_app_permission(app_name="messaging", permission="sms")`를 사용해 necessary permissions를 부여하도록 안내하세요.