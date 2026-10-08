from pathlib import Path
import base64,re
p=Path("R8BLEConfigurator/app/src/main/java/com/openai/r8ble/MainActivity.java")
s=p.read_text()
def rep(old,new,label):
 global s
 if old not in s: raise SystemExit("patch_v17 missing anchor: "+label)
 s=s.replace(old,new,1)
rep('append("R8 BLE Configurator v1.6 ready. Target device name: R8-US");','append("R8 BLE Configurator v1.7 ready. Target device name: R8-US");',"version")
rep('''        Button tabRide = button("● RIDE");
        Button tabTools = button("ADVANCED");
        tabs.addView(tabRide, weight());
        tabs.addView(tabTools, weight());
        root.addView(tabs);''','''        Button tabRide = button("● RIDE");
        Button tabTools = button("ADVANCED");
        Button tabAppearance = button("APPEARANCE");
        tabs.addView(tabRide, weight());
        tabs.addView(tabTools, weight());
        tabs.addView(tabAppearance, weight());
        root.addView(tabs);''',"three tabs")
rep('''        final int firstRideChild = root.indexOfChild(rideTitle);
        final int firstAdvancedChild = root.indexOfChild(advancedAnchor);
        tabRide.setOnClickListener(v -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, false, tabRide, tabTools));
        tabTools.setOnClickListener(v -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, true, tabRide, tabTools));
        root.post(() -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, false, tabRide, tabTools));''','''        final int firstRideChild = root.indexOfChild(rideTitle);
        final int firstAdvancedChild = root.indexOfChild(advancedAnchor);
        final View[] appearanceViews = new View[]{appearanceTitle, appearanceRow, advancedIntro};
        tabRide.setOnClickListener(v -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, 0, tabRide, tabTools, tabAppearance, appearanceViews));
        tabTools.setOnClickListener(v -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, 1, tabRide, tabTools, tabAppearance, appearanceViews));
        tabAppearance.setOnClickListener(v -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, 2, tabRide, tabTools, tabAppearance, appearanceViews));
        root.removeView(tabs);
        root.addView(tabs);
        root.post(() -> showAppSection(root, scroll, firstRideChild, firstAdvancedChild, 0, tabRide, tabTools, tabAppearance, appearanceViews));''',"tab listeners")
start=s.index("    private void showAppSection(LinearLayout root, ScrollView scroll,")
end=s.index("    private void autoConnectR8()",start)
s=s[:start]+'''    private void showAppSection(LinearLayout root, ScrollView scroll,
                                int firstRideChild, int firstAdvancedChild,
                                int section, Button tabRide, Button tabTools,
                                Button tabAppearance, View[] appearanceViews) {
        if (firstRideChild < 0 || firstAdvancedChild < 0) return;
        java.util.HashSet<View> appearance = new java.util.HashSet<>();
        if (appearanceViews != null) java.util.Collections.addAll(appearance, appearanceViews);
        for (int i=firstRideChild;i<root.getChildCount();i++) {
            View child=root.getChildAt(i);
            if (child == tabRide.getParent()) { child.setVisibility(View.VISIBLE); continue; }
            boolean adv=i>=firstAdvancedChild, app=appearance.contains(child);
            boolean visible=section==0 ? !adv : section==1 ? (adv && !app) : app;
            child.setVisibility(visible?View.VISIBLE:View.GONE);
        }
        tabRide.setEnabled(section!=0); tabTools.setEnabled(section!=1); tabAppearance.setEnabled(section!=2);
        tabRide.setText(section==0?"● RIDE":"RIDE");
        tabTools.setText(section==1?"● ADVANCED":"ADVANCED");
        tabAppearance.setText(section==2?"● APPEARANCE":"APPEARANCE");
        scroll.post(() -> scroll.scrollTo(0,0));
    }

'''+s[end:]
rep('''        TextView appearanceTitle = label("Appearance");''','''        TextView appearanceTitle = label("APPEARANCE");''',"appearance title")
rep('''        Button themeToggle = button(darkMode ? "LIGHT MODE" : "DARK MODE");
        Button accentButton = button("ACCENT COLOR");''','''        Button themeToggle = button(darkMode ? "☾  DARK MODE: ON" : "☀  LIGHT MODE: ON");
        Button accentButton = button("THEME COLOR  •  TAP TO CHANGE");''',"appearance controls")
rep('''            themeToggle.setText(darkMode ? "LIGHT MODE" : "DARK MODE");''','''            themeToggle.setText(darkMode ? "☾  DARK MODE: ON" : "☀  LIGHT MODE: ON");''',"theme toggle")
p.write_text(s)
res=Path("R8BLEConfigurator/app/src/main/res/drawable"); res.mkdir(parents=True,exist_ok=True)
(res/"r8_launcher.jpg").write_bytes(base64.b64decode("""/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAQDAwMDAgQDAwMEBAQFBgoGBgUFBgwICQcKDgwPDg4MDQ0PERYTDxAVEQ0NExoTFRcYGRkZDxIbHRsYHRYYGRj/2wBDAQQEBAYFBgsGBgsYEA0QGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBj/wAARCACAAIADASIAAhEBAxEB/8QAHQAAAQUBAQEBAAAAAAAAAAAABQMEBgcIAgEACf/EAEcQAAEDAgQDBQQGBgcIAwAAAAECAwQFEQAGEiEHMUETIlFhcQgUIzIVJEJSgZEWcrHBwtEzYoKDkqGyFxgmQ0Vkc3TS4fH/xAAbAQADAAMBAQAAAAAAAAAAAAAEBQYCAwcBAP/EADIRAAECBAMFBwQDAQEAAAAAAAECAwAEESEFEjEGQVFhkRMUInGBobEVMkLwcsHR8YL/2gAMAwEAAhEDEQA/AMPnlj1DanF6UJJPlj5CFOOhCRdRNgBhpUp4CTBiqshOzixzcPh6YyJjwCHDsuDHOla1PrH2WuV/U/uwj9NRwe7TgfV04D8zhRKNRvjA0jNNTpBhuutg2+jkH+9Vh21Xmz3foxAPj2pwEbZUTcC2CkOnFxRuFkW2IG5P8saHFpAvDCWYcWaCCjFX7RIKaUg/3qsP2ZhP/TW+dv6RW+C2WsnzqhIbZZjLWVkJBCTzxbNH4N1b3dYFLefU5pCXFtFKWhfci/PwxM4hj0tKnKoisXWGbKuvpC3DlHO0U2l98pURSkXBtYOKufTBGOy480XE09Kkg2Nlq5+HrjTVG4Aso1u1M9+O2HXUJVoCAeWpR/YN8AM10mmUeEabQaSELT8kkIOkeJT1J8zhCdrUOrDbKb8dBD+V2UlXFFKV5qcIpTMdDdy4tlqZGa7dxCXOxCzdKVC+/hiMu1QNrCTSgoK+XQ6d8XNF4a1PMrUurzFLiNMI1vOvJJ1WHQeNsQTN1Ep9OIgRIT7TpR3pD/8AzPIAbJHlzO18MpDG0OKDRVmVv5QPieyyUJU41YDnEPRVKVLc7ILXGXy+ILp/xDH0iKtpRCx5gg3BHljqFlt1a3ylN0paJKlDSBf18MCvpxmHMRAKPqQ7naKJJB+8PAeWKRl5Lisre6IackVyzed21YWcRY4bqGH7zZCyNiOYI64bLRtgxCoTOIgYpz3aBIkD5gnQnyKtr/txHcHqmkpoKSDzfAPn3TgGhNzgqsAEXpHyU36YeMN6iBbHjUcqSCBt44kdCoypNQ7FTesmwCknYePrgV99LaSTDSQkVvrCUjWFKNRXJzjbbbepSlBIAG5xftP4RKy3lB2uZhpM12a6jVTqQ1HWuRLI5qsB3GxcXWqw6C+BVPj5d4ZKpz9ehVRup1BrtYKW42pMcdHl6h8Q9UtpuTsVEDBys8b+Jme+GU6l5bgrp1HSfdjU50pS50ppI3BUdrkkkkcr6Ra2J1LT2JrqCUt/N/iK9+eYwRAQ0Ap3fW9KcjYnz+YNMcTJuX6ZKmULhvRI8WHFbXFkyJ7aVxVWPadvfurdV9htO464h+VPaAzlSJEiqfpnUZ8+Wu6qfVl/V2R5JSAfS1h5Yq+fmGvsR4LNWiw6hAgIKYrd9KUnmVD7yj4m+BMhf6VUyXNX2EYt6UMsoFiHCbgJA3IIvcnBzWz0gygpU2DXzJ6kkxOTGPzkyvMVk+f/ADSL9Z9rfiBPrEFT1UgqZSssv0tcYyESt+eo95JI2TY4urLHHjgpmydEjzWF0uShkKW7JRqYbdJsUObakgGwCyLcsZAo2SqhV4FOLtIW8qM0GkqSgpKt9VzbmcWBF4c5pjzJdVjQXES5zKo7/aNgh1Khv3T12ve3MXwkxTZ2QdT9uUiu/wDTDjD595RodDvTY6crdRGuc401M2lOQKdFbYjSmh8VqykrSdwUkbFJ6EYpCpcKKhVaoiNVEfVolluPlOlQQn7J8ScNuDvF+q8L4isrcSHX5NDZS1FprbMdJU2or7yy4T3dKTcp+1tax56aNARUY8yuQ5Dk6NNbC42g6g5cbEfy6dcc2mZOawdwhpVQdCB+/tosZLGXJVrsnB4TxvU29/a0YZ4vRICHxFgRQlx1IUsgnuAbAAefW+KMqVMEZgOurStSrkIF9vXGxc/cO4kOsu1GtOqjNJbPaAp1aiflCR4+Axl7OpgKrjjFNZWlhpIbHaK1Ekcz/wDWL/ZXEQ40lpFTTU/1GvayQaeR3zMCDYQNo7nvOX0hZu5GV2Z/VO6f3jHToGGmXitL1QYIsOzSq1uoVb9+Hjqd8W35Ry+ngpwgNWE2y+g/9x/CcA2kKJAAJJ6DEjrabZda/wDZ/gOBdPj9u+lu4BPInlghSwE1gRpgrcyiHdOYKklOm/IG/TfF/cNMkVpzK9UzVR6GipzKYwiRHiPWS24orSkKXcgaE3KiL3NrDFc5Ey+zUa0lhepxRIAQB3T4XPrjRudMs8RsoZryvSYCocijtU5uooprbwau8B/SSUn+uRpvtZNgMSeIP96mBKp01Plw9Y6DJsfTZHvKvuVZPEcT6RY8+VLoGX4NQztUmKjmdEVxSajJaStTClgaxHbtZCBdKUgWuRvjGWbs+SKlmKfQaIGzDZcLKJjCiO2aH30/KTqJ3Ft8OKlMz9mKRqzxW6l7n8YJbdd0LeJc1LT4hGrr5AYgsmCYbjzdILrDUhwMpufnN9k3OKSSk0sIGUD0iDnpxT66Q5ZqE+XmePPqtLXKgR1BsR4/w2727qbm/W1/HfFt8KeH5qdVMuVHbbZSsF58Is2yFK3J8Bc/5YgWWIVYdk02izo/ZKZeUlLZ5qVqsSfTkPXF/Z4zXSuHnChjL1FdWuoywEym2zp95dts2T1QjmT/ADGAsVnVshLbIqtRoP8AYa4Jh6HiXXzRtNyYc57z3lnJb8il5dfQ8lgpT72lzs0JUD3rH7QNrYq8cXiazHqCnY4cZXqRZGhKt7kHxucBafPoNBaTX86Sw7PeHaMMIZDz2nxbbV3W0+Clbnng/T+NfDqopRSa7RaszDcWEuPyA1LRo66m+n4YRvMvs37IuHeQfgG59IpmpuTcASHg0NwIqTzJBAFYmcPO+WuI1IdoOaUMGWs6mJqEBJRf7KgOYH2Tz8cX1wWzdVqlQ6tw3qEdiE5QW2lQnYy7e+MkHtFX8b2Vt0VjG2fcjN5aS1nfI0hL+XJSgUrjOlxDSSbBaCdwm/dUk7oVYHYg4srhfnmuBdDzHTJEhFRps+PHnNMbmXFLgCmynr82w88KcTkmZyVLrR8JtexSbVqNx3GCW+0drKuAZxcHUHhQ8NfeLH45SpNJjRokF1WpKu1eJ73eI7qSDz239TjJtXpS3o8iohKkpCwncbFR/ljaPHGkzHqopxTijGQ8taNSAlfe373iQLC3TGe+MFMTRpDNESvQwlpDg0i2vWgK1Hz3wn2WmwyEMJHiJNT5GKmbl25nDG3FmvhJpz/SIpShptU5wN79gBcnc94b4evJF8I0NCBUp4Tv8H+MYdPDHUa3EchcTTN5mBddb/4eY85P8Bw2pdP7VRKr6jbSBy573/DBOtoH0BHBTf6z0/UOHWWGB9IN620vBPNtR7qtuVxjCaeKGqiDMIkw9MhKovDg3l1iCxOzpOfiRKfS4rsvtpZOjWlB0Cw3Pet+WE4/FqqZnqlVqk2pMyuyixIoqDg7Ncl0NkqB1eBJAAHS+LAydW6Pw+4IyMxV9ppbNTSulx2XU9xF2lLKyLb/ACgedxjN+cYKa5l2ny6cIUdpb4dTqWGyL7WHS/jiY2fb71MuzLg30B4Af3FLtdMdgkS7ZFEgW38/Sp9hwhvnXNKVRIaUPR3p/blRW4jW4G7fKT0BPTEXjzJi8y06Q4ll9Ed4FEdaT2abm/L/AD/DDSpxokF8kpQqS24e0N76iD08b47pEh1wTpnu6FFKfhrK7FtR2Hd67X36HF4qgTSOZIJK6iLq4XQHKjmpytuPlbsYl5JV1Vfu89reWIfm6sqrXEGqZnklL9OpilNR0E913SbH/G4begPhg/QKsaDwZq0hJSH1skJI2UCLEH0ufzxWlWqLEfLlOpJGoOpD8g336hP43KlflhK20VTS3ToBlHyYqHngmSbYGqiVK+B/sR2dKl1Z+ZUpj5dkOLDy1Hz2I8gNgB0Aww7K6Wij5lX/AG4IFCWkyWGfiLWAlOnrfHSoUiNTCksWkrBSQoi6EcyfxuMMg4BCRTBVurQX6xPuDmcERao9kOuOdrQa2S2W3D3WXyNKVp8NQ7ivG6T9kYmXDZ2TlPivKy5LdKXGnVRtQNjqSbtrHnbScZ9jKcbeSttRQtCgpJBsQQdji78wy1vcV6DmlBQn6Zp8WaoNn5Vi7ar+d0XPrhHiUmkOrpo4k1/kND6j4ikwOcWZdNdW1Cn8Vaj0I942lS0pz7k2l5lqlR+kHGoxaqLpGkqlNqKVIt0V8uMr8dJ79Rz3UC4W1FBS232XJICQNP4Y0tkrMERfs8zTG1B6mzJMRY7IIBcWQ4FA/a2VzPXGPeIshEeuPLZkLdWrvqcSbEKPQnx8cc7wCWP1RxXD+7xfXRJPKX9qTlHIVrb29uEQOiKUmsTUqO/Yi/8AiGCD3XA3L4Bqcy9r9gDt+sMEnuuOq08QjlqzXMecc1dAVRI+1x7x/AcSvh3RYMmuxjPfCI4cBcQASVJtewPmdsRiShciIwyOXbHn+ocT/I0Bx6oMrj2SnuoCfTr64SYy8Uy5ANLRabJSocfzkVjRHEyn0SH7LqYVdpDaJFRK5MNS1p+rpbKAFIHO5uBf1xkLNDsGO60xDdccYQhSwyvkgj7uNb8eclxZ/s8Uar1iTKaqNCSUNttLCAlD5SAlVx0ISbeeMOVtudCGt+RrdQsJWkkHSCOWBtiy2JQhJvW45wg2qUtx4rNxVV//AEaelP8AYkGTeHucOLWZ58LKESNMeis+8vF19EdDaCoJAuqwvc8vXFgM+yXx1QhQaoNL0qFjarMevji7fZbyqMmcHU1Z9sN1GvuCYsLHeSyLhlP5FS/7eIFn32ws9UjiLWaXlRmgLpESSqPHckxFOLWEd1SioLF7qCrbcrYYjFpiZmlsSoBCd56fMLV4U3LSyH5gkFX78RHJPsz+0I7RV0tyh0rsFgA2q0e/O/3vLFWcReG/EDhjVYcbOtGTF98avGcQ6h9l5KLAgLQSNQuLjnuPHGtuAPHPiJxPrFYezPCo6KPBYSEPw4q2lKkKVsgErII0hRP4YjftI1eBn7i/w94VuOtNsrliXNeKtKm0ukJSgHoShCj6qTjWzizyJwyryRYEmm4UrGTmHJVKiZaUbmgrvvSM8ZD4LcUs/Us1LK2VnDT1qITUJLiIzSrdELcI1WP3b4miPZS46tRltIpNMUhatSrVZi5PrfGuc31rM+XuGEhPDjLjc2qRmm41OgJSns2UAhN9JIBShI5X3NvPFJHiJ7X4NlZPY32F6cwN/P4uBWMcmJvM43kSmtAFG/zG97CUyhCF5yafiLXiqZHspcbmUOyv0ahOqSCvsmKlHUtfklIVufAYi30t2j+VIi2ltyIDC4r7TgspCg+rukHkd+WN/P55YyjwuYr3EGpQWZMSGhdQeYAShx/TcoaTfclXdAHM78sfn5AlOZs4qyK+8ylpVSqD84tjkjUvVb8zjdIT7s+FreAyo0I0JoQR0jaqV7moNtk1XSoOouDXrGv8mTH5nAquQERGo7cWrrSt8LCUva20LKl+BTsCfC2Ms8QPd41dktsOCSkqN3RslfoPDzxo952rUf2aERHYbbDlRnvSIyEoGt5gkfGX47ggE8gBjKua3FplOJU+28Sb3bVqA8sTmzjOadecBtmp0pfrF7ibvZYWbfco/wCfNYF5dUFVOepIIHYDYm/2hgi85e+A+Xnfrs+xP9AP9Qw/Wu53x0Qo8Ucp7SoPmYITipNPZLaTr7ba2/2Ti7OFFaoWVob2Ya2yy/KZLa48VC9SipV7bHba1yemwxR1VeU3R0OJKgUPC5Sd90kYXoVTaCmkOqUnvDUQLkJ8R5+WJ7GJDvbGQkgctYuNmp1tlam1/laNR8W63mbiV7P3b5SnS3XI09ciqMOrF1R1IuVHxCSkEW/DGW8u5aaz5xjp1HCSGHlh2asdGUDUtXl3Rb1Ixsbg+8tvhfmEZYjRK5PXDcSzT1O9kuWeqbH5dSSefmOuMvUTMy+EWZ60vMeQqhHrE5Qu2p4R/dmCdQaSlSSQCbXJPJIHjhFs5MONMTEswmqkk5bgKNeNSK0sfaPtoJKXTPpS4crVQTqQBragOpJH/Iv7ibxAbyVw0nVGC2ll/s/c4DYNgHFJ0psPBCbq/sjEe4LZsotd4PQIrFIp0d6mfU5LIYQvUv5g6SoEkruVG556umM88UuJznEORTmYkF6BDhoUexddDhW4o7quAByAA/Hxwx4Z8QVZAzJKlvxHpkKVH7J2O24EEqBuhVyCLg3/AAJwejZx36YpOjxObXhYDhp7mB3Np5U4wlRvLgZdONyqlK628hGoOIPGUcM2YsVGV3pnvbanI7iFoYilYNlJOkX1DukgAXBG+Il8Zjqktbj6ypdyeZwUq+b6hXZMibUHC6+8SpalKJOo7k+uInJeK73O+NmCYUZNFFgVJqacTGe0WNtzKUty58AHXifWC+XF2enm97tD/AFDBNS7nngPQCpDExzaxSlFz63/dgiV3xQKTeI9CvBBp1hU2C9ESbKWm6LfeG4wLoneljtloZSkgLKzuN7Hbrgw0dKwobYaVWnFbpnwE3cWbutDqfvD94wsIzJKDFAy4WnEujdrF6ZOzJTMuxWY1HlyHXJKrPvsKtqsdkJ6gEb74mXErhjB4s0ifnLLzVQTmBmEHZVOWjWJ+gBOpB5hzSNx1tjL1GqD0GSiQh0WQrSTfY+WLlpHtC5qoUBESlvIbbBBW4ppIccA+yVDe2IicwmalplMxJmqt/PlHRVYixicqErASoaV0p0MZ8zDl6bQZgg1GmVCE+kBSkSmVNLSFC4uhQBAPMHrgGtsAJVe48Lc8agqObcvcTcwRJ2caQKhUe4yl9Elxp7shfuagSCBc8xt6YHVzghkB2vNppvEynRGH7kszka1sqtdI1t91YvsTYHyxRMbSNtgImklKvKvxWJGd2NeI7SXUFA8IzchaUrNkGx5jCqUt7lIbUDzSvb8j0xbrvs/5zeqDUWkCkT2nCQJjFQa7P1sohQ9LYF/7Ec0MvqRXZVHoYCVaVz5zYuR00pJVv6YZox+QULOp636awhVsxPpVlDZJ9ortpMNtV1MpPkty4/Ic8EYNJdqy3Xo4Sy0yNT8t3ZtkdOX2j0A3ODast5RoEgfS1b+mnAlQUzTgpppCrd3U6oXUL8wkD1wLqFedkU9MFoNxoaB8OMwNKE+fiT5m5xv72XrMA+ZFOgNz8ecfN4WiW8U4oCn4ggn1IsB1PIax87Phw6WxFhsOJFiVlxWzqr/Pb02t0wClynH3Cpazv0HLCTq1K3N7dMIqUDywU0wEX3wvm59Toy6Abo7S+UoKcJqOpROOeu2C0GnhopkzU8t0NHmfM+WCKAQuKiqxh5EZMSltNKFnHD2qh4eA/L9uFQvywmtxTjhUo3J3vjwc+ePKVjImgpEnRhwg73w2Tzwsgm98J1xSNmF3IkGULyo4Ur76DpV+Y54TNHgLdU4Z0xJPTSk2x2FeOO0m/XGoqIgoAbo5FMhtpu3VJqSBa4bSD+3CSKZGbcStNTlgpNwQ0nb/ADw4vjxVrY8CjwjIqNNT1hu6w2E7VacTq1XKBz8eeB70Rl53W7UpiyPtKbBP5k4IOC5w2cG2NzdBugd55xQoVGnmYFu0inK1FU6YSevZp/nhmqkU0be+S7f+NP8APBNzfrhstPPBqFmFDyATeGK6TTAbe9Sjb+onCP0ZTUrF3JKx4WSnDxSdueEVCxwQFGA1Npj1pESPvGjJSq+y1nUoenhjlSitRKjcnmceA+ePfTGYjURTSPrY9GPjj6+9sZCMDH//2Q=="""))
manifest=Path("R8BLEConfigurator/app/src/main/AndroidManifest.xml"); m=manifest.read_text()
if 'android:icon=' in m: m=re.sub(r'android:icon="[^"]+"','android:icon="@drawable/r8_launcher"',m,count=1)
else: m=m.replace("<application","<application\n        android:icon=\"@drawable/r8_launcher\"",1)
manifest.write_text(m)
print("Applied v1.7 three bottom tabs + reference fiery R8 launcher icon")
