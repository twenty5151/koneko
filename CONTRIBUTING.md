# Contributing
* Fork it
* Edit the files on your fork/branch
    * If your git client complains about committing to master, just remove `.pre-commit-config.yaml`
* Run tests with `pytest testing/ -vvvv -l -s`
* Try it with `python setup.py install` then `koneko` to simulate a pip install (or `pip install .`; check out [manual installation](#manual-installation))
    * If doing the latter, make sure you aren't running the released version on pypi (totally didn't happen to me).
* Submit a pull request
* If you want to, you can create an issue first. Ask any questions by opening a new issue.
* If you're encountering/fixing a bug and you're stuck, try clearing the cache. For example, a bug might have downloaded to the wrong folder, but after fixing the bug, you need to clear the cache, otherwise it would not download anything and display the wrong contents.


## Priorities
(As in, what I think I need help on and what you might want to focus on, not what will only be accepted. All PRs will be considered, regardless if it's important or not)

1. Speed: if it's slower than going to pixiv then half of its purpose is gone
    * The bottleneck is network IO and downloading images from pixiv
2. Reliable rendering: There's no point in browsing a media-heavy site if the terminal is text-only and can't render the images well
    * While it's working perfectly for my use case, it should work well for other reasonable cases (different terminal sizes, number+name for the gallery)

Flowchart of modes and their connections:

![Flowchart UML](http://plantuml.com:80/plantuml/png/dPDD2y8m38Rl_HM5dZtejfk8YYY2Dy6BY1IDTHWtwGVYltVMhfkrAdWgIzuyUPUcGwMvrEQCX1W5Eww0ZgJEbTuAZWZorlNn-PaBwFdFQObONlD2RBajK8bFBO7BtR6Efmq1qLJaGrsPDKsjZIvb4u3BydGRem4I6A7zphgTtyXS77Ldu6f_oYkb-uNNhZtA5lnQp2H04ONuR0lnFCAq0mOD4ig4XR-Fp094pGud7pCZ0YDVcURYB2M1fPGo2NiIN9IjhE8nBv-alaKQjUjeqS5db3qkPfMN29gyBOUjRmJjuV-I8XpyOcHHN_znwuqBXqE6KEohHtG7)

Simplified UML diagram of the classes:

![Classes UML](http://plantuml.com:80/plantuml/png/bLXVZzmc47_dK_2OR6D_WEYqIjIeRQfMYjG_BrLbSJQxIuur572kf_I-UmSm633svbwYOpo_6MRcDpDitcb3b9ck72733AVuIjZOoYU4oBqsYlG6zvneZT_Fnr-4aFZkxjNxDrZHuVNn-1LX_DtNeFtixBrwZPuHce7AC6r-5GDrKAiE07m5WVzpGOZxpnGSCiudRRgJu5myTbQnum15AB_3VyqW7iUcSF0Mi_525JEwglxNXGq37Vzkjhma-0qDt2XslfXewOZ_PFJnarZkyEt8_EweD8GRJaylqYyT_4Q9wYz_QAhq2r0_k8kpyPm3IqvCh0qv_f5mJjNJYXbGtv7-Qpf9pXHgx0HIqIzmXKmc91qxpiQ7hXT23Nej7wTh4Df2Sa66Zbt1H84eFYOmvzH9WqHHgnbE2ualP1muxQGILvcHsKRiIf34-_qRt3-HSGbuZOxWZuuOFhrx9iwY8yvFT_PQHP3hxqcSQ_yvRGvpuvJ1lCKz88IcsdVd5eqJV2MUbPKQIsvOY2ru0rnSFuFLKhqYUcaZr7dL8djZIvB-0KW5ncQrUOvvaeELBgBcBmFJafCdJyQC7rPGPGJEUHrgZLs3v2BNSBd8jPoOT27cb7oXdj_rsLhc8SdnAaLjUon3pezE8mI9iXpiVRfhsygaGQ5KzLcrMp0Fh8p6NLGzGtNtDxPGKtEUyZSI8ZUVCsFHIgmLAjiJEsgNytgPBJOBWIlrAMuf9JS7wfAxjT-bYVCGaopiWPA84qIz68TjN_cegXJbiE6oc75bdhdkYOct_nt-UQ2gbcmiYRduFoSv44CJWdeZ3lnXRduT6GhR02uo7yvqf8eOeNQnzkgtyMZZxiscpQG0By9kp7cNuKDhyzxk-8mLi4EciYSExIGttEPGj9chPfB9hgYfxM1pS6s0XRtX5tM-EoQmCMzm9rxtWfkOYLQA3e-2ke6uI7sEZwLwQia_ed8xyvBoQ81dEiznC0ERIJlx-bcBCL8FH6vewAud_MMUixYVbAAZdp7sDLE8_Lia4DO11sybtNgJukMwN1eCdvZITZEUYuRpyyokgSzmpo2OXw3BCOippGVhpizfe2ufMPZBNKwCqv5SGwIpuVbrnOOu2RB0uQzxy2nEMPHE2Io7CoSA10DJHTXqVYVezDRX7Y4MUxRfoMOyfCSw2BAGVo_AGhP4p28k8c13Nc7hEfVKYkIq4gOamTfZ-XbU2Sn8mKRpBGKk6GA4jGde9EjJ9pvLYs150s3uYje7wFQcqcF9hB4OL50bmfoegXoJl79HRYA72Sr792X--lYJ-ocmJ7qGT_zCTAB9sLmK9SCYo7Utpy4ZOGRU_cSMkqCIfQ7OaDAYN-8mkQMWADn4c-Kz8GnC74jStnW3DOH57fx2vlQLAC3QxURgf_n7pARJG4LVu29zrTyDQHaGUaV7mVutoly0)

<details>
  <summary>Actor-ish model of the ui.Gallery class</summary>
  
  ![Gallery UML](http://plantuml.com:80/plantuml/png/bLLDRzim3BthLt2t16qFQT6BWRGTMc3OWBL1Y-vgQ1QJQB4bJPBJ1il--_HbnuxT0CibClb4FZsHr9snLDkwAedbjaJuGiiIzGugoT30nF_13AXWS3qbX1PMQdWrg0cPp-6xzneiiR1S2fZFYNV1nGtK7CxEiWYOWTjpJPpfmday8eFFPWDBPwuzdhCsaHJbRfgYX30PBFWxtpeCOTJIdzGWhFoA51gfRJvyy9kupa3H5UQYhiwXebpaYjfr0b0LUNrxUNe4ZRzhD9PejBKMZSqeAGps0xwuKpirMcTANPg2seGCQtSkni1gMcoSGj71v9ie9MKPFAGLyCeHD5vCllLn6WXf5ct0GFQhXyEbWmaSGXh_BFhZjbRd1svKINSn9SnEkoy_ZdwLikEGzCcGLzqj1xrQz49pOO6BfIGhBMi5IkCIRR7cOaN0_Jht4CGG-6xpMfV1cMwkP-jVjABQk5fmWCcqkwL_sKU9CdXLp1DslP3xOZ9vGOjr5pTognuO44E9l7LCEXIigRw5bfMoPB_VXyvwKYYIXCEkEZZ9iJp1clCsxF6ttueC_fHSRFv-QjFrItCaPHymIAkaiVal8qMJvs0urgjPvP7Q5ZLVScJkUaRwOKIpcA1b_kYkDaW_GZhu5WtVumergG_FNSsv8ZIn2YDTFtUwbNYKTA5nosLjFagiaZyKZpjP4kLauYRsCmQTXq5rSBXeaMAQenfX9simjSRRpeuCxgLOSbrHFvdxq-o-HAe7jPquFcDu44nu05fIFpY-fTgOh2HOcJuyQ3h2zO3_dr9f1ppl3dZU6V1yV1vt5M5Hv5XUasaIEMhSQmeLEixf6Gv9xbmp-cUGa7y0)
  
</details>

<details>
  <summary>Actor-ish model of the ui.Image class</summary>
  
  ![Image UML](http://plantuml.com:80/plantuml/png/bLHDJyCm3BtdLvWRQ73XMAbeIBk0n3PfshaAZJiYkYJ4ITd4-Eya_Tf71nezLCvxp-wp7NLCZbldroLpqfK8Jsk-GdZH0XbBqpe0mX9p9xM2D6KyTzh2aj2o-8Ax1_0IHgEaqTwpS0fOv19uf7SeWjn7fHG76GdCvKPM4MmIk6cgF2zcKx3uuP4Si-YyLHr6HYj29hZZhvmmv8QeJQ_Z11R17D9Usv12VwfISv70f8r0nZufTYChxh2NC853hBKnaMHAlgKc-HQCbSg5aoeqs-rszS1c1bN3ns6TJ6XFTYKZWWA-IgdUlw_wAiSsprGw5WpQxAAifhCAhImaYkkRVpNSsvdYnlrgHGKoCu4BrKzzSDggFElTa95AeRtOHYpNtwM_fh-osXkOMopGvM-rfNOo49w36x9tBDUhpDko5hJB6E0NjnF5G_iHFTVMYQS4baOS2h3T6p5KWrs49YkfFO4vlmxJyjrABhsxu_2j-1jWFm00)

</details>

<details>
  <summary>Actor-ish model of the ui.User class</summary>
  
  ![User UML](http://plantuml.com:80/plantuml/png/VLHDJzmm4BtxLymHX3Z0zXHfAQX8g9LALqKzHsuokrWaTZgs5rRQ7r-FFx9Pmf93vCnxRpuplhLEalDz9vno7S8VYsJXh3SjmW8CmPTp8PPB-Ca6YnqsJXaDowMGZGimymM_uF86l8ABYofnarW4qsL0c571dNs1TJ1xvgiswwAmWfLwKrksikG6v92S_NZwzGY4_pnQ9mYT9rriTZ3QecYbat-bHV1y4WsXTEKZ-Ohd2fv2mcWFmipiR2DTPiPpIBHjmP5iNa9n2MZDg-wCR2kupoTGlToWvJweBVif554EeyDOo7UcmtMWQPnJ2dwLy2GR6tUlxD39NGe9Lv_3rwUzBt9qd2VzgSl5L9BwjI7Z1nW8r-YQPwKt0i8pwNSiMkERgprr4SpJEx8T3tkGPB5cmjdvL78yy7U1veCz44wFZJdpBh3re-wWRilFjoBJ3qxiz_ku68yXsP1tQ5BOYNUB4B5Lm8xNm3wRrvebeSXSH_Z_Iojpd370Yd2hZBUdWWmPBnvpcjCWnTM3WR3ioZg8-pttjJ5r8jHCEAGtpZEZlC2r6bloiVKkMXzaro7jnXn-Ovp2F3P5O8oPRmn2s1aFrXD-dIWg-6RqMb4l-JeQQ-QxhDGhRiFG-68JuZy0)
  
</details>

## Conda environment

See [MANUAL.md](MANUAL.md#conda-environment)

## Manual installation

Note: if you want to make some edits, you should install it in a conda environment. See above

```sh
# Use the latest stable version (recommended for usage)
# Make sure the version number is the latest
git clone -b 'v0.6.2' --depth 1 https://github.com/twenty5151/koneko.git
# Use the master branch for upcoming features:
git clone -b master https://github.com/twenty5151/koneko.git
# Use the dev branch for latest features, fixes, and instability (recommended for contributers):
git clone -b dev https://github.com/twenty5151/koneko.git

# Run the tests (for those who want to edit)
# Add --inte for integration testing, but don't be surprised if it fails
pytest testing/ -vvvv -l -s 

cd koneko
# Manually install without PyPI; for general usage
# Both will correctly copy the required pictures
pip install .
# or
python setup.py install
# or
# Manually install for development, changes will be immediately reflected
python setup.py develop

# On certain shells with implicit cd, typing `koneko` might cd into the dir
# Instead of running the executable
cd ~
# Use anywhere:
koneko
```

## Unit tests
Run `pytest testing/ -vvvv -l -s`. Add `--inte` for integration testing, but don't be surprised if it fails

## Build and upload to PyPI
When test installing with pip, don't forget to use `pip install .` or `python setup.py install`, not `pip install koneko` (which will grab from latest stable version). (Yes, I made the same mistake again)

**Warning:** ~~you~~ *must* test installing with `pip install .`, `python setup.py install`, `python setup.py develop`, and `python -m koneko.main` (but now it's automated).

Bump version info in `__init__.py`, `setup.py`, and `README.md`

```sh
python setup.py sdist bdist_wheel
twine upload dist/*
pip install koneko --upgrade
```