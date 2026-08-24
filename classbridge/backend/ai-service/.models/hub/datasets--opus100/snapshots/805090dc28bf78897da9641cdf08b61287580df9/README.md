---
annotations_creators:
- no-annotation
language_creators:
- found
language:
- af
- am
- an
- ar
- as
- az
- be
- bg
- bn
- br
- bs
- ca
- cs
- cy
- da
- de
- dz
- el
- en
- eo
- es
- et
- eu
- fa
- fi
- fr
- fy
- ga
- gd
- gl
- gu
- ha
- he
- hi
- hr
- hu
- hy
- id
- ig
- is
- it
- ja
- ka
- kk
- km
- kn
- ko
- ku
- ky
- li
- lt
- lv
- mg
- mk
- ml
- mn
- mr
- ms
- mt
- my
- nb
- ne
- nl
- nn
- 'no'
- oc
- or
- pa
- pl
- ps
- pt
- ro
- ru
- rw
- se
- sh
- si
- sk
- sl
- sq
- sr
- sv
- ta
- te
- tg
- th
- tk
- tr
- tt
- ug
- uk
- ur
- uz
- vi
- wa
- xh
- yi
- yo
- zh
- zu
license:
- unknown
multilinguality:
- translation
size_categories:
- 100K<n<1M
- 10K<n<100K
- 1K<n<10K
- 1M<n<10M
- n<1K
source_datasets:
- extended
task_categories:
- translation
task_ids: []
paperswithcode_id: opus-100
pretty_name: OPUS-100
config_names:
- af-en
- am-en
- an-en
- ar-de
- ar-en
- ar-fr
- ar-nl
- ar-ru
- ar-zh
- as-en
- az-en
- be-en
- bg-en
- bn-en
- br-en
- bs-en
- ca-en
- cs-en
- cy-en
- da-en
- de-en
- de-fr
- de-nl
- de-ru
- de-zh
- dz-en
- el-en
- en-eo
- en-es
- en-et
- en-eu
- en-fa
- en-fi
- en-fr
- en-fy
- en-ga
- en-gd
- en-gl
- en-gu
- en-ha
- en-he
- en-hi
- en-hr
- en-hu
- en-hy
- en-id
- en-ig
- en-is
- en-it
- en-ja
- en-ka
- en-kk
- en-km
- en-kn
- en-ko
- en-ku
- en-ky
- en-li
- en-lt
- en-lv
- en-mg
- en-mk
- en-ml
- en-mn
- en-mr
- en-ms
- en-mt
- en-my
- en-nb
- en-ne
- en-nl
- en-nn
- en-no
- en-oc
- en-or
- en-pa
- en-pl
- en-ps
- en-pt
- en-ro
- en-ru
- en-rw
- en-se
- en-sh
- en-si
- en-sk
- en-sl
- en-sq
- en-sr
- en-sv
- en-ta
- en-te
- en-tg
- en-th
- en-tk
- en-tr
- en-tt
- en-ug
- en-uk
- en-ur
- en-uz
- en-vi
- en-wa
- en-xh
- en-yi
- en-yo
- en-zh
- en-zu
- fr-nl
- fr-ru
- fr-zh
- nl-ru
- nl-zh
- ru-zh
dataset_info:
- config_name: af-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - af
        - en
  splits:
  - name: test
    num_bytes: 135908
    num_examples: 2000
  - name: train
    num_bytes: 18726247
    num_examples: 275512
  - name: validation
    num_bytes: 132769
    num_examples: 2000
  download_size: 14852797
  dataset_size: 18994924
- config_name: am-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - am
        - en
  splits:
  - name: test
    num_bytes: 588021
    num_examples: 2000
  - name: train
    num_bytes: 21950572
    num_examples: 89027
  - name: validation
    num_bytes: 566069
    num_examples: 2000
  download_size: 12630031
  dataset_size: 23104662
- config_name: an-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - an
        - en
  splits:
  - name: train
    num_bytes: 438324
    num_examples: 6961
  download_size: 232976
  dataset_size: 438324
- config_name: ar-de
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ar
        - de
  splits:
  - name: test
    num_bytes: 238591
    num_examples: 2000
  download_size: 161557
  dataset_size: 238591
- config_name: ar-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ar
        - en
  splits:
  - name: test
    num_bytes: 331640
    num_examples: 2000
  - name: train
    num_bytes: 152765684
    num_examples: 1000000
  - name: validation
    num_bytes: 2272098
    num_examples: 2000
  download_size: 100486814
  dataset_size: 155369422
- config_name: ar-fr
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ar
        - fr
  splits:
  - name: test
    num_bytes: 547374
    num_examples: 2000
  download_size: 334226
  dataset_size: 547374
- config_name: ar-nl
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ar
        - nl
  splits:
  - name: test
    num_bytes: 212928
    num_examples: 2000
  download_size: 144863
  dataset_size: 212928
- config_name: ar-ru
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ar
        - ru
  splits:
  - name: test
    num_bytes: 808262
    num_examples: 2000
  download_size: 441536
  dataset_size: 808262
- config_name: ar-zh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ar
        - zh
  splits:
  - name: test
    num_bytes: 713404
    num_examples: 2000
  download_size: 438598
  dataset_size: 713404
- config_name: as-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - as
        - en
  splits:
  - name: test
    num_bytes: 261458
    num_examples: 2000
  - name: train
    num_bytes: 15634536
    num_examples: 138479
  - name: validation
    num_bytes: 248131
    num_examples: 2000
  download_size: 8794616
  dataset_size: 16144125
- config_name: az-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - az
        - en
  splits:
  - name: test
    num_bytes: 393101
    num_examples: 2000
  - name: train
    num_bytes: 56431043
    num_examples: 262089
  - name: validation
    num_bytes: 407101
    num_examples: 2000
  download_size: 34988859
  dataset_size: 57231245
- config_name: be-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - be
        - en
  splits:
  - name: test
    num_bytes: 166850
    num_examples: 2000
  - name: train
    num_bytes: 5298444
    num_examples: 67312
  - name: validation
    num_bytes: 175197
    num_examples: 2000
  download_size: 3807669
  dataset_size: 5640491
- config_name: bg-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - bg
        - en
  splits:
  - name: test
    num_bytes: 243743
    num_examples: 2000
  - name: train
    num_bytes: 108929547
    num_examples: 1000000
  - name: validation
    num_bytes: 234840
    num_examples: 2000
  download_size: 71575310
  dataset_size: 109408130
- config_name: bn-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - bn
        - en
  splits:
  - name: test
    num_bytes: 510093
    num_examples: 2000
  - name: train
    num_bytes: 249906046
    num_examples: 1000000
  - name: validation
    num_bytes: 498406
    num_examples: 2000
  download_size: 134076596
  dataset_size: 250914545
- config_name: br-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - br
        - en
  splits:
  - name: test
    num_bytes: 127917
    num_examples: 2000
  - name: train
    num_bytes: 8538878
    num_examples: 153447
  - name: validation
    num_bytes: 133764
    num_examples: 2000
  download_size: 6881865
  dataset_size: 8800559
- config_name: bs-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - bs
        - en
  splits:
  - name: test
    num_bytes: 168614
    num_examples: 2000
  - name: train
    num_bytes: 75082148
    num_examples: 1000000
  - name: validation
    num_bytes: 172473
    num_examples: 2000
  download_size: 59514403
  dataset_size: 75423235
- config_name: ca-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ca
        - en
  splits:
  - name: test
    num_bytes: 205658
    num_examples: 2000
  - name: train
    num_bytes: 88404710
    num_examples: 1000000
  - name: validation
    num_bytes: 212629
    num_examples: 2000
  download_size: 68438385
  dataset_size: 88822997
- config_name: cs-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - cs
        - en
  splits:
  - name: test
    num_bytes: 205266
    num_examples: 2000
  - name: train
    num_bytes: 91896919
    num_examples: 1000000
  - name: validation
    num_bytes: 219076
    num_examples: 2000
  download_size: 73028514
  dataset_size: 92321261
- config_name: cy-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - cy
        - en
  splits:
  - name: test
    num_bytes: 124281
    num_examples: 2000
  - name: train
    num_bytes: 17244748
    num_examples: 289521
  - name: validation
    num_bytes: 118848
    num_examples: 2000
  download_size: 13398765
  dataset_size: 17487877
- config_name: da-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - da
        - en
  splits:
  - name: test
    num_bytes: 298115
    num_examples: 2000
  - name: train
    num_bytes: 126424474
    num_examples: 1000000
  - name: validation
    num_bytes: 300616
    num_examples: 2000
  download_size: 91005252
  dataset_size: 127023205
- config_name: de-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - de
        - en
  splits:
  - name: test
    num_bytes: 330951
    num_examples: 2000
  - name: train
    num_bytes: 152245956
    num_examples: 1000000
  - name: validation
    num_bytes: 332342
    num_examples: 2000
  download_size: 116680890
  dataset_size: 152909249
- config_name: de-fr
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - de
        - fr
  splits:
  - name: test
    num_bytes: 458738
    num_examples: 2000
  download_size: 311929
  dataset_size: 458738
- config_name: de-nl
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - de
        - nl
  splits:
  - name: test
    num_bytes: 403878
    num_examples: 2000
  download_size: 281548
  dataset_size: 403878
- config_name: de-ru
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - de
        - ru
  splits:
  - name: test
    num_bytes: 315771
    num_examples: 2000
  download_size: 203225
  dataset_size: 315771
- config_name: de-zh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - de
        - zh
  splits:
  - name: test
    num_bytes: 280389
    num_examples: 2000
  download_size: 215301
  dataset_size: 280389
- config_name: dz-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - dz
        - en
  splits:
  - name: train
    num_bytes: 81154
    num_examples: 624
  download_size: 37361
  dataset_size: 81154
- config_name: el-en
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - el
        - en
  splits:
  - name: test
    num_bytes: 302385
    num_examples: 2000
  - name: train
    num_bytes: 127963903
    num_examples: 1000000
  - name: validation
    num_bytes: 291226
    num_examples: 2000
  download_size: 84137722
  dataset_size: 128557514
- config_name: en-eo
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - eo
  splits:
  - name: test
    num_bytes: 167378
    num_examples: 2000
  - name: train
    num_bytes: 24431681
    num_examples: 337106
  - name: validation
    num_bytes: 168830
    num_examples: 2000
  download_size: 19545461
  dataset_size: 24767889
- config_name: en-es
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - es
  splits:
  - name: test
    num_bytes: 326262
    num_examples: 2000
  - name: train
    num_bytes: 136643104
    num_examples: 1000000
  - name: validation
    num_bytes: 326727
    num_examples: 2000
  download_size: 100103907
  dataset_size: 137296093
- config_name: en-et
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - et
  splits:
  - name: test
    num_bytes: 272163
    num_examples: 2000
  - name: train
    num_bytes: 112298253
    num_examples: 1000000
  - name: validation
    num_bytes: 276954
    num_examples: 2000
  download_size: 83690450
  dataset_size: 112847370
- config_name: en-eu
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - eu
  splits:
  - name: test
    num_bytes: 280877
    num_examples: 2000
  - name: train
    num_bytes: 112329285
    num_examples: 1000000
  - name: validation
    num_bytes: 281495
    num_examples: 2000
  download_size: 84805467
  dataset_size: 112891657
- config_name: en-fa
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - fa
  splits:
  - name: test
    num_bytes: 296548
    num_examples: 2000
  - name: train
    num_bytes: 125400535
    num_examples: 1000000
  - name: validation
    num_bytes: 291121
    num_examples: 2000
  download_size: 82783248
  dataset_size: 125988204
- config_name: en-fi
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - fi
  splits:
  - name: test
    num_bytes: 245814
    num_examples: 2000
  - name: train
    num_bytes: 106024990
    num_examples: 1000000
  - name: validation
    num_bytes: 247219
    num_examples: 2000
  download_size: 79320220
  dataset_size: 106518023
- config_name: en-fr
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - fr
  splits:
  - name: test
    num_bytes: 469723
    num_examples: 2000
  - name: train
    num_bytes: 201440450
    num_examples: 1000000
  - name: validation
    num_bytes: 481476
    num_examples: 2000
  download_size: 142251860
  dataset_size: 202391649
- config_name: en-fy
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - fy
  splits:
  - name: test
    num_bytes: 101238
    num_examples: 2000
  - name: train
    num_bytes: 3895640
    num_examples: 54342
  - name: validation
    num_bytes: 100121
    num_examples: 2000
  download_size: 2984283
  dataset_size: 4096999
- config_name: en-ga
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ga
  splits:
  - name: test
    num_bytes: 503309
    num_examples: 2000
  - name: train
    num_bytes: 42132510
    num_examples: 289524
  - name: validation
    num_bytes: 503209
    num_examples: 2000
  download_size: 27937448
  dataset_size: 43139028
- config_name: en-gd
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - gd
  splits:
  - name: test
    num_bytes: 218354
    num_examples: 1606
  - name: train
    num_bytes: 1254779
    num_examples: 16316
  - name: validation
    num_bytes: 203877
    num_examples: 1605
  download_size: 1124506
  dataset_size: 1677010
- config_name: en-gl
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - gl
  splits:
  - name: test
    num_bytes: 190691
    num_examples: 2000
  - name: train
    num_bytes: 43327028
    num_examples: 515344
  - name: validation
    num_bytes: 193598
    num_examples: 2000
  download_size: 34084028
  dataset_size: 43711317
- config_name: en-gu
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - gu
  splits:
  - name: test
    num_bytes: 199725
    num_examples: 2000
  - name: train
    num_bytes: 33641719
    num_examples: 318306
  - name: validation
    num_bytes: 205542
    num_examples: 2000
  download_size: 19235779
  dataset_size: 34046986
- config_name: en-ha
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ha
  splits:
  - name: test
    num_bytes: 407344
    num_examples: 2000
  - name: train
    num_bytes: 20391884
    num_examples: 97983
  - name: validation
    num_bytes: 411518
    num_examples: 2000
  download_size: 12686187
  dataset_size: 21210746
- config_name: en-he
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - he
  splits:
  - name: test
    num_bytes: 208467
    num_examples: 2000
  - name: train
    num_bytes: 91159631
    num_examples: 1000000
  - name: validation
    num_bytes: 209438
    num_examples: 2000
  download_size: 61144758
  dataset_size: 91577536
- config_name: en-hi
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - hi
  splits:
  - name: test
    num_bytes: 496570
    num_examples: 2000
  - name: train
    num_bytes: 124923545
    num_examples: 534319
  - name: validation
    num_bytes: 474079
    num_examples: 2000
  download_size: 65725886
  dataset_size: 125894194
- config_name: en-hr
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - hr
  splits:
  - name: test
    num_bytes: 179636
    num_examples: 2000
  - name: train
    num_bytes: 75309516
    num_examples: 1000000
  - name: validation
    num_bytes: 179615
    num_examples: 2000
  download_size: 59468892
  dataset_size: 75668767
- config_name: en-hu
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - hu
  splits:
  - name: test
    num_bytes: 206039
    num_examples: 2000
  - name: train
    num_bytes: 87483462
    num_examples: 1000000
  - name: validation
    num_bytes: 208307
    num_examples: 2000
  download_size: 67971116
  dataset_size: 87897808
- config_name: en-hy
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - hy
  splits:
  - name: train
    num_bytes: 652623
    num_examples: 7059
  download_size: 422847
  dataset_size: 652623
- config_name: en-id
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - id
  splits:
  - name: test
    num_bytes: 177685
    num_examples: 2000
  - name: train
    num_bytes: 78698973
    num_examples: 1000000
  - name: validation
    num_bytes: 180024
    num_examples: 2000
  download_size: 57693678
  dataset_size: 79056682
- config_name: en-ig
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ig
  splits:
  - name: test
    num_bytes: 137324
    num_examples: 1843
  - name: train
    num_bytes: 1612523
    num_examples: 18415
  - name: validation
    num_bytes: 135987
    num_examples: 1843
  download_size: 859440
  dataset_size: 1885834
- config_name: en-is
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - is
  splits:
  - name: test
    num_bytes: 170879
    num_examples: 2000
  - name: train
    num_bytes: 73964115
    num_examples: 1000000
  - name: validation
    num_bytes: 170632
    num_examples: 2000
  download_size: 56242149
  dataset_size: 74305626
- config_name: en-it
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - it
  splits:
  - name: test
    num_bytes: 299029
    num_examples: 2000
  - name: train
    num_bytes: 123654286
    num_examples: 1000000
  - name: validation
    num_bytes: 294354
    num_examples: 2000
  download_size: 92133897
  dataset_size: 124247669
- config_name: en-ja
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ja
  splits:
  - name: test
    num_bytes: 190991
    num_examples: 2000
  - name: train
    num_bytes: 88348569
    num_examples: 1000000
  - name: validation
    num_bytes: 191411
    num_examples: 2000
  download_size: 64817108
  dataset_size: 88730971
- config_name: en-ka
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ka
  splits:
  - name: test
    num_bytes: 256219
    num_examples: 2000
  - name: train
    num_bytes: 42465402
    num_examples: 377306
  - name: validation
    num_bytes: 260408
    num_examples: 2000
  download_size: 24394633
  dataset_size: 42982029
- config_name: en-kk
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - kk
  splits:
  - name: test
    num_bytes: 137656
    num_examples: 2000
  - name: train
    num_bytes: 7124314
    num_examples: 79927
  - name: validation
    num_bytes: 139657
    num_examples: 2000
  download_size: 4808360
  dataset_size: 7401627
- config_name: en-km
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - km
  splits:
  - name: test
    num_bytes: 289019
    num_examples: 2000
  - name: train
    num_bytes: 19680515
    num_examples: 111483
  - name: validation
    num_bytes: 302519
    num_examples: 2000
  download_size: 10022919
  dataset_size: 20272053
- config_name: en-kn
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - kn
  splits:
  - name: test
    num_bytes: 77197
    num_examples: 918
  - name: train
    num_bytes: 1833318
    num_examples: 14537
  - name: validation
    num_bytes: 77599
    num_examples: 917
  download_size: 1062554
  dataset_size: 1988114
- config_name: en-ko
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ko
  splits:
  - name: test
    num_bytes: 190688
    num_examples: 2000
  - name: train
    num_bytes: 93664532
    num_examples: 1000000
  - name: validation
    num_bytes: 189360
    num_examples: 2000
  download_size: 70383271
  dataset_size: 94044580
- config_name: en-ku
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ku
  splits:
  - name: test
    num_bytes: 247839
    num_examples: 2000
  - name: train
    num_bytes: 49107744
    num_examples: 144844
  - name: validation
    num_bytes: 239317
    num_examples: 2000
  download_size: 25358389
  dataset_size: 49594900
- config_name: en-ky
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ky
  splits:
  - name: test
    num_bytes: 142522
    num_examples: 2000
  - name: train
    num_bytes: 1879274
    num_examples: 27215
  - name: validation
    num_bytes: 138479
    num_examples: 2000
  download_size: 1338686
  dataset_size: 2160275
- config_name: en-li
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - li
  splits:
  - name: test
    num_bytes: 93342
    num_examples: 2000
  - name: train
    num_bytes: 1628577
    num_examples: 25535
  - name: validation
    num_bytes: 92898
    num_examples: 2000
  download_size: 1040760
  dataset_size: 1814817
- config_name: en-lt
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - lt
  splits:
  - name: test
    num_bytes: 482607
    num_examples: 2000
  - name: train
    num_bytes: 177060244
    num_examples: 1000000
  - name: validation
    num_bytes: 469109
    num_examples: 2000
  download_size: 124444053
  dataset_size: 178011960
- config_name: en-lv
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - lv
  splits:
  - name: test
    num_bytes: 536568
    num_examples: 2000
  - name: train
    num_bytes: 206051049
    num_examples: 1000000
  - name: validation
    num_bytes: 522064
    num_examples: 2000
  download_size: 140538527
  dataset_size: 207109681
- config_name: en-mg
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - mg
  splits:
  - name: test
    num_bytes: 525059
    num_examples: 2000
  - name: train
    num_bytes: 130865169
    num_examples: 590771
  - name: validation
    num_bytes: 511163
    num_examples: 2000
  download_size: 91102165
  dataset_size: 131901391
- config_name: en-mk
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - mk
  splits:
  - name: test
    num_bytes: 308926
    num_examples: 2000
  - name: train
    num_bytes: 117068689
    num_examples: 1000000
  - name: validation
    num_bytes: 305490
    num_examples: 2000
  download_size: 76810811
  dataset_size: 117683105
- config_name: en-ml
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ml
  splits:
  - name: test
    num_bytes: 340618
    num_examples: 2000
  - name: train
    num_bytes: 199971079
    num_examples: 822746
  - name: validation
    num_bytes: 334451
    num_examples: 2000
  download_size: 95497482
  dataset_size: 200646148
- config_name: en-mn
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - mn
  splits:
  - name: train
    num_bytes: 250770
    num_examples: 4294
  download_size: 85037
  dataset_size: 250770
- config_name: en-mr
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - mr
  splits:
  - name: test
    num_bytes: 238604
    num_examples: 2000
  - name: train
    num_bytes: 2724107
    num_examples: 27007
  - name: validation
    num_bytes: 235532
    num_examples: 2000
  download_size: 1838618
  dataset_size: 3198243
- config_name: en-ms
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ms
  splits:
  - name: test
    num_bytes: 179697
    num_examples: 2000
  - name: train
    num_bytes: 76828845
    num_examples: 1000000
  - name: validation
    num_bytes: 180175
    num_examples: 2000
  download_size: 57412836
  dataset_size: 77188717
- config_name: en-mt
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - mt
  splits:
  - name: test
    num_bytes: 566126
    num_examples: 2000
  - name: train
    num_bytes: 222221596
    num_examples: 1000000
  - name: validation
    num_bytes: 594378
    num_examples: 2000
  download_size: 147836637
  dataset_size: 223382100
- config_name: en-my
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - my
  splits:
  - name: test
    num_bytes: 337343
    num_examples: 2000
  - name: train
    num_bytes: 3673477
    num_examples: 24594
  - name: validation
    num_bytes: 336147
    num_examples: 2000
  download_size: 1952573
  dataset_size: 4346967
- config_name: en-nb
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - nb
  splits:
  - name: test
    num_bytes: 334109
    num_examples: 2000
  - name: train
    num_bytes: 13611589
    num_examples: 142906
  - name: validation
    num_bytes: 324392
    num_examples: 2000
  download_size: 10630769
  dataset_size: 14270090
- config_name: en-ne
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ne
  splits:
  - name: test
    num_bytes: 186519
    num_examples: 2000
  - name: train
    num_bytes: 44135952
    num_examples: 406381
  - name: validation
    num_bytes: 204912
    num_examples: 2000
  download_size: 24107523
  dataset_size: 44527383
- config_name: en-nl
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - nl
  splits:
  - name: test
    num_bytes: 282747
    num_examples: 2000
  - name: train
    num_bytes: 112326273
    num_examples: 1000000
  - name: validation
    num_bytes: 270932
    num_examples: 2000
  download_size: 82923916
  dataset_size: 112879952
- config_name: en-nn
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - nn
  splits:
  - name: test
    num_bytes: 178999
    num_examples: 2000
  - name: train
    num_bytes: 32924429
    num_examples: 486055
  - name: validation
    num_bytes: 187642
    num_examples: 2000
  download_size: 25184676
  dataset_size: 33291070
- config_name: en-no
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - 'no'
  splits:
  - name: test
    num_bytes: 173320
    num_examples: 2000
  - name: train
    num_bytes: 74105483
    num_examples: 1000000
  - name: validation
    num_bytes: 178005
    num_examples: 2000
  download_size: 56277000
  dataset_size: 74456808
- config_name: en-oc
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - oc
  splits:
  - name: test
    num_bytes: 82342
    num_examples: 2000
  - name: train
    num_bytes: 1627174
    num_examples: 35791
  - name: validation
    num_bytes: 81642
    num_examples: 2000
  download_size: 1308338
  dataset_size: 1791158
- config_name: en-or
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - or
  splits:
  - name: test
    num_bytes: 163939
    num_examples: 1318
  - name: train
    num_bytes: 1500733
    num_examples: 14273
  - name: validation
    num_bytes: 155323
    num_examples: 1317
  download_size: 1019971
  dataset_size: 1819995
- config_name: en-pa
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - pa
  splits:
  - name: test
    num_bytes: 133901
    num_examples: 2000
  - name: train
    num_bytes: 8509140
    num_examples: 107296
  - name: validation
    num_bytes: 136188
    num_examples: 2000
  download_size: 5315298
  dataset_size: 8779229
- config_name: en-pl
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - pl
  splits:
  - name: test
    num_bytes: 212495
    num_examples: 2000
  - name: train
    num_bytes: 95247723
    num_examples: 1000000
  - name: validation
    num_bytes: 218208
    num_examples: 2000
  download_size: 73574044
  dataset_size: 95678426
- config_name: en-ps
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ps
  splits:
  - name: test
    num_bytes: 92995
    num_examples: 2000
  - name: train
    num_bytes: 4436512
    num_examples: 79127
  - name: validation
    num_bytes: 95156
    num_examples: 2000
  download_size: 2851899
  dataset_size: 4624663
- config_name: en-pt
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - pt
  splits:
  - name: test
    num_bytes: 296114
    num_examples: 2000
  - name: train
    num_bytes: 118242849
    num_examples: 1000000
  - name: validation
    num_bytes: 292074
    num_examples: 2000
  download_size: 87661907
  dataset_size: 118831037
- config_name: en-ro
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ro
  splits:
  - name: test
    num_bytes: 198639
    num_examples: 2000
  - name: train
    num_bytes: 85249051
    num_examples: 1000000
  - name: validation
    num_bytes: 199164
    num_examples: 2000
  download_size: 66294317
  dataset_size: 85646854
- config_name: en-ru
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ru
  splits:
  - name: test
    num_bytes: 490976
    num_examples: 2000
  - name: train
    num_bytes: 195100937
    num_examples: 1000000
  - name: validation
    num_bytes: 490238
    num_examples: 2000
  download_size: 124460816
  dataset_size: 196082151
- config_name: en-rw
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - rw
  splits:
  - name: test
    num_bytes: 136189
    num_examples: 2000
  - name: train
    num_bytes: 15286159
    num_examples: 173823
  - name: validation
    num_bytes: 134957
    num_examples: 2000
  download_size: 10093708
  dataset_size: 15557305
- config_name: en-se
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - se
  splits:
  - name: test
    num_bytes: 85697
    num_examples: 2000
  - name: train
    num_bytes: 2047380
    num_examples: 35907
  - name: validation
    num_bytes: 83664
    num_examples: 2000
  download_size: 1662845
  dataset_size: 2216741
- config_name: en-sh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - sh
  splits:
  - name: test
    num_bytes: 569479
    num_examples: 2000
  - name: train
    num_bytes: 60900023
    num_examples: 267211
  - name: validation
    num_bytes: 555594
    num_examples: 2000
  download_size: 39988454
  dataset_size: 62025096
- config_name: en-si
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - si
  splits:
  - name: test
    num_bytes: 271735
    num_examples: 2000
  - name: train
    num_bytes: 114950891
    num_examples: 979109
  - name: validation
    num_bytes: 271236
    num_examples: 2000
  download_size: 66124160
  dataset_size: 115493862
- config_name: en-sk
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - sk
  splits:
  - name: test
    num_bytes: 258034
    num_examples: 2000
  - name: train
    num_bytes: 111743068
    num_examples: 1000000
  - name: validation
    num_bytes: 255462
    num_examples: 2000
  download_size: 85223330
  dataset_size: 112256564
- config_name: en-sl
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - sl
  splits:
  - name: test
    num_bytes: 205470
    num_examples: 2000
  - name: train
    num_bytes: 90270157
    num_examples: 1000000
  - name: validation
    num_bytes: 198654
    num_examples: 2000
  download_size: 70708189
  dataset_size: 90674281
- config_name: en-sq
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - sq
  splits:
  - name: test
    num_bytes: 275371
    num_examples: 2000
  - name: train
    num_bytes: 105745181
    num_examples: 1000000
  - name: validation
    num_bytes: 267304
    num_examples: 2000
  download_size: 78817895
  dataset_size: 106287856
- config_name: en-sr
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - sr
  splits:
  - name: test
    num_bytes: 180224
    num_examples: 2000
  - name: train
    num_bytes: 75726035
    num_examples: 1000000
  - name: validation
    num_bytes: 184238
    num_examples: 2000
  download_size: 60263688
  dataset_size: 76090497
- config_name: en-sv
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - sv
  splits:
  - name: test
    num_bytes: 271006
    num_examples: 2000
  - name: train
    num_bytes: 116985153
    num_examples: 1000000
  - name: validation
    num_bytes: 279986
    num_examples: 2000
  download_size: 85032127
  dataset_size: 117536145
- config_name: en-ta
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ta
  splits:
  - name: test
    num_bytes: 351982
    num_examples: 2000
  - name: train
    num_bytes: 74044340
    num_examples: 227014
  - name: validation
    num_bytes: 335549
    num_examples: 2000
  download_size: 33642694
  dataset_size: 74731871
- config_name: en-te
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - te
  splits:
  - name: test
    num_bytes: 190587
    num_examples: 2000
  - name: train
    num_bytes: 6688569
    num_examples: 64352
  - name: validation
    num_bytes: 193658
    num_examples: 2000
  download_size: 4047667
  dataset_size: 7072814
- config_name: en-tg
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - tg
  splits:
  - name: test
    num_bytes: 372112
    num_examples: 2000
  - name: train
    num_bytes: 35477017
    num_examples: 193882
  - name: validation
    num_bytes: 371720
    num_examples: 2000
  download_size: 21242668
  dataset_size: 36220849
- config_name: en-th
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - th
  splits:
  - name: test
    num_bytes: 290573
    num_examples: 2000
  - name: train
    num_bytes: 132820231
    num_examples: 1000000
  - name: validation
    num_bytes: 288358
    num_examples: 2000
  download_size: 75539987
  dataset_size: 133399162
- config_name: en-tk
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - tk
  splits:
  - name: test
    num_bytes: 83878
    num_examples: 1852
  - name: train
    num_bytes: 719617
    num_examples: 13110
  - name: validation
    num_bytes: 81006
    num_examples: 1852
  download_size: 417756
  dataset_size: 884501
- config_name: en-tr
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - tr
  splits:
  - name: test
    num_bytes: 183825
    num_examples: 2000
  - name: train
    num_bytes: 78945565
    num_examples: 1000000
  - name: validation
    num_bytes: 181909
    num_examples: 2000
  download_size: 60364921
  dataset_size: 79311299
- config_name: en-tt
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - tt
  splits:
  - name: test
    num_bytes: 693268
    num_examples: 2000
  - name: train
    num_bytes: 35313170
    num_examples: 100843
  - name: validation
    num_bytes: 701662
    num_examples: 2000
  download_size: 18786998
  dataset_size: 36708100
- config_name: en-ug
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ug
  splits:
  - name: test
    num_bytes: 620873
    num_examples: 2000
  - name: train
    num_bytes: 31576516
    num_examples: 72170
  - name: validation
    num_bytes: 631228
    num_examples: 2000
  download_size: 16011372
  dataset_size: 32828617
- config_name: en-uk
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - uk
  splits:
  - name: test
    num_bytes: 249742
    num_examples: 2000
  - name: train
    num_bytes: 104229556
    num_examples: 1000000
  - name: validation
    num_bytes: 247123
    num_examples: 2000
  download_size: 71155682
  dataset_size: 104726421
- config_name: en-ur
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - ur
  splits:
  - name: test
    num_bytes: 538556
    num_examples: 2000
  - name: train
    num_bytes: 268960696
    num_examples: 753913
  - name: validation
    num_bytes: 529308
    num_examples: 2000
  download_size: 148336044
  dataset_size: 270028560
- config_name: en-uz
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - uz
  splits:
  - name: test
    num_bytes: 408675
    num_examples: 2000
  - name: train
    num_bytes: 38375290
    num_examples: 173157
  - name: validation
    num_bytes: 398853
    num_examples: 2000
  download_size: 21873536
  dataset_size: 39182818
- config_name: en-vi
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - vi
  splits:
  - name: test
    num_bytes: 192744
    num_examples: 2000
  - name: train
    num_bytes: 82614470
    num_examples: 1000000
  - name: validation
    num_bytes: 194721
    num_examples: 2000
  download_size: 59250852
  dataset_size: 83001935
- config_name: en-wa
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - wa
  splits:
  - name: test
    num_bytes: 87091
    num_examples: 2000
  - name: train
    num_bytes: 6085860
    num_examples: 104496
  - name: validation
    num_bytes: 87718
    num_examples: 2000
  download_size: 4512204
  dataset_size: 6260669
- config_name: en-xh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - xh
  splits:
  - name: test
    num_bytes: 318652
    num_examples: 2000
  - name: train
    num_bytes: 50606896
    num_examples: 439671
  - name: validation
    num_bytes: 315831
    num_examples: 2000
  download_size: 37519365
  dataset_size: 51241379
- config_name: en-yi
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - yi
  splits:
  - name: test
    num_bytes: 96482
    num_examples: 2000
  - name: train
    num_bytes: 1275127
    num_examples: 15010
  - name: validation
    num_bytes: 99818
    num_examples: 2000
  download_size: 650530
  dataset_size: 1471427
- config_name: en-yo
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - yo
  splits:
  - name: train
    num_bytes: 979753
    num_examples: 10375
  download_size: 391299
  dataset_size: 979753
- config_name: en-zh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - zh
  splits:
  - name: test
    num_bytes: 511364
    num_examples: 2000
  - name: train
    num_bytes: 200062183
    num_examples: 1000000
  - name: validation
    num_bytes: 512356
    num_examples: 2000
  download_size: 143414756
  dataset_size: 201085903
- config_name: en-zu
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - en
        - zu
  splits:
  - name: test
    num_bytes: 117510
    num_examples: 2000
  - name: train
    num_bytes: 2799558
    num_examples: 38616
  - name: validation
    num_bytes: 120133
    num_examples: 2000
  download_size: 1918443
  dataset_size: 3037201
- config_name: fr-nl
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - fr
        - nl
  splits:
  - name: test
    num_bytes: 368638
    num_examples: 2000
  download_size: 261290
  dataset_size: 368638
- config_name: fr-ru
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - fr
        - ru
  splits:
  - name: test
    num_bytes: 732716
    num_examples: 2000
  download_size: 426179
  dataset_size: 732716
- config_name: fr-zh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - fr
        - zh
  splits:
  - name: test
    num_bytes: 619386
    num_examples: 2000
  download_size: 418661
  dataset_size: 619386
- config_name: nl-ru
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - nl
        - ru
  splits:
  - name: test
    num_bytes: 256059
    num_examples: 2000
  download_size: 168666
  dataset_size: 256059
- config_name: nl-zh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - nl
        - zh
  splits:
  - name: test
    num_bytes: 183633
    num_examples: 2000
  download_size: 146191
  dataset_size: 183633
- config_name: ru-zh
  features:
  - name: translation
    dtype:
      translation:
        languages:
        - ru
        - zh
  splits:
  - name: test
    num_bytes: 916106
    num_examples: 2000
  download_size: 534430
  dataset_size: 916106
configs:
- config_name: af-en
  data_files:
  - split: test
    path: af-en/test-*
  - split: train
    path: af-en/train-*
  - split: validation
    path: af-en/validation-*
- config_name: am-en
  data_files:
  - split: test
    path: am-en/test-*
  - split: train
    path: am-en/train-*
  - split: validation
    path: am-en/validation-*
- config_name: an-en
  data_files:
  - split: train
    path: an-en/train-*
- config_name: ar-de
  data_files:
  - split: test
    path: ar-de/test-*
- config_name: ar-en
  data_files:
  - split: test
    path: ar-en/test-*
  - split: train
    path: ar-en/train-*
  - split: validation
    path: ar-en/validation-*
- config_name: ar-fr
  data_files:
  - split: test
    path: ar-fr/test-*
- config_name: ar-nl
  data_files:
  - split: test
    path: ar-nl/test-*
- config_name: ar-ru
  data_files:
  - split: test
    path: ar-ru/test-*
- config_name: ar-zh
  data_files:
  - split: test
    path: ar-zh/test-*
- config_name: as-en
  data_files:
  - split: test
    path: as-en/test-*
  - split: train
    path: as-en/train-*
  - split: validation
    path: as-en/validation-*
- config_name: az-en
  data_files:
  - split: test
    path: az-en/test-*
  - split: train
    path: az-en/train-*
  - split: validation
    path: az-en/validation-*
- config_name: be-en
  data_files:
  - split: test
    path: be-en/test-*
  - split: train
    path: be-en/train-*
  - split: validation
    path: be-en/validation-*
- config_name: bg-en
  data_files:
  - split: test
    path: bg-en/test-*
  - split: train
    path: bg-en/train-*
  - split: validation
    path: bg-en/validation-*
- config_name: bn-en
  data_files:
  - split: test
    path: bn-en/test-*
  - split: train
    path: bn-en/train-*
  - split: validation
    path: bn-en/validation-*
- config_name: br-en
  data_files:
  - split: test
    path: br-en/test-*
  - split: train
    path: br-en/train-*
  - split: validation
    path: br-en/validation-*
- config_name: bs-en
  data_files:
  - split: test
    path: bs-en/test-*
  - split: train
    path: bs-en/train-*
  - split: validation
    path: bs-en/validation-*
- config_name: ca-en
  data_files:
  - split: test
    path: ca-en/test-*
  - split: train
    path: ca-en/train-*
  - split: validation
    path: ca-en/validation-*
- config_name: cs-en
  data_files:
  - split: test
    path: cs-en/test-*
  - split: train
    path: cs-en/train-*
  - split: validation
    path: cs-en/validation-*
- config_name: cy-en
  data_files:
  - split: test
    path: cy-en/test-*
  - split: train
    path: cy-en/train-*
  - split: validation
    path: cy-en/validation-*
- config_name: da-en
  data_files:
  - split: test
    path: da-en/test-*
  - split: train
    path: da-en/train-*
  - split: validation
    path: da-en/validation-*
- config_name: de-en
  data_files:
  - split: test
    path: de-en/test-*
  - split: train
    path: de-en/train-*
  - split: validation
    path: de-en/validation-*
- config_name: de-fr
  data_files:
  - split: test
    path: de-fr/test-*
- config_name: de-nl
  data_files:
  - split: test
    path: de-nl/test-*
- config_name: de-ru
  data_files:
  - split: test
    path: de-ru/test-*
- config_name: de-zh
  data_files:
  - split: test
    path: de-zh/test-*
- config_name: dz-en
  data_files:
  - split: train
    path: dz-en/train-*
- config_name: el-en
  data_files:
  - split: test
    path: el-en/test-*
  - split: train
    path: el-en/train-*
  - split: validation
    path: el-en/validation-*
- config_name: en-eo
  data_files:
  - split: test
    path: en-eo/test-*
  - split: train
    path: en-eo/train-*
  - split: validation
    path: en-eo/validation-*
- config_name: en-es
  data_files:
  - split: test
    path: en-es/test-*
  - split: train
    path: en-es/train-*
  - split: validation
    path: en-es/validation-*
- config_name: en-et
  data_files:
  - split: test
    path: en-et/test-*
  - split: train
    path: en-et/train-*
  - split: validation
    path: en-et/validation-*
- config_name: en-eu
  data_files:
  - split: test
    path: en-eu/test-*
  - split: train
    path: en-eu/train-*
  - split: validation
    path: en-eu/validation-*
- config_name: en-fa
  data_files:
  - split: test
    path: en-fa/test-*
  - split: train
    path: en-fa/train-*
  - split: validation
    path: en-fa/validation-*
- config_name: en-fi
  data_files:
  - split: test
    path: en-fi/test-*
  - split: train
    path: en-fi/train-*
  - split: validation
    path: en-fi/validation-*
- config_name: en-fr
  data_files:
  - split: test
    path: en-fr/test-*
  - split: train
    path: en-fr/train-*
  - split: validation
    path: en-fr/validation-*
- config_name: en-fy
  data_files:
  - split: test
    path: en-fy/test-*
  - split: train
    path: en-fy/train-*
  - split: validation
    path: en-fy/validation-*
- config_name: en-ga
  data_files:
  - split: test
    path: en-ga/test-*
  - split: train
    path: en-ga/train-*
  - split: validation
    path: en-ga/validation-*
- config_name: en-gd
  data_files:
  - split: test
    path: en-gd/test-*
  - split: train
    path: en-gd/train-*
  - split: validation
    path: en-gd/validation-*
- config_name: en-gl
  data_files:
  - split: test
    path: en-gl/test-*
  - split: train
    path: en-gl/train-*
  - split: validation
    path: en-gl/validation-*
- config_name: en-gu
  data_files:
  - split: test
    path: en-gu/test-*
  - split: train
    path: en-gu/train-*
  - split: validation
    path: en-gu/validation-*
- config_name: en-ha
  data_files:
  - split: test
    path: en-ha/test-*
  - split: train
    path: en-ha/train-*
  - split: validation
    path: en-ha/validation-*
- config_name: en-he
  data_files:
  - split: test
    path: en-he/test-*
  - split: train
    path: en-he/train-*
  - split: validation
    path: en-he/validation-*
- config_name: en-hi
  data_files:
  - split: test
    path: en-hi/test-*
  - split: train
    path: en-hi/train-*
  - split: validation
    path: en-hi/validation-*
- config_name: en-hr
  data_files:
  - split: test
    path: en-hr/test-*
  - split: train
    path: en-hr/train-*
  - split: validation
    path: en-hr/validation-*
- config_name: en-hu
  data_files:
  - split: test
    path: en-hu/test-*
  - split: train
    path: en-hu/train-*
  - split: validation
    path: en-hu/validation-*
- config_name: en-hy
  data_files:
  - split: train
    path: en-hy/train-*
- config_name: en-id
  data_files:
  - split: test
    path: en-id/test-*
  - split: train
    path: en-id/train-*
  - split: validation
    path: en-id/validation-*
- config_name: en-ig
  data_files:
  - split: test
    path: en-ig/test-*
  - split: train
    path: en-ig/train-*
  - split: validation
    path: en-ig/validation-*
- config_name: en-is
  data_files:
  - split: test
    path: en-is/test-*
  - split: train
    path: en-is/train-*
  - split: validation
    path: en-is/validation-*
- config_name: en-it
  data_files:
  - split: test
    path: en-it/test-*
  - split: train
    path: en-it/train-*
  - split: validation
    path: en-it/validation-*
- config_name: en-ja
  data_files:
  - split: test
    path: en-ja/test-*
  - split: train
    path: en-ja/train-*
  - split: validation
    path: en-ja/validation-*
- config_name: en-ka
  data_files:
  - split: test
    path: en-ka/test-*
  - split: train
    path: en-ka/train-*
  - split: validation
    path: en-ka/validation-*
- config_name: en-kk
  data_files:
  - split: test
    path: en-kk/test-*
  - split: train
    path: en-kk/train-*
  - split: validation
    path: en-kk/validation-*
- config_name: en-km
  data_files:
  - split: test
    path: en-km/test-*
  - split: train
    path: en-km/train-*
  - split: validation
    path: en-km/validation-*
- config_name: en-kn
  data_files:
  - split: test
    path: en-kn/test-*
  - split: train
    path: en-kn/train-*
  - split: validation
    path: en-kn/validation-*
- config_name: en-ko
  data_files:
  - split: test
    path: en-ko/test-*
  - split: train
    path: en-ko/train-*
  - split: validation
    path: en-ko/validation-*
- config_name: en-ku
  data_files:
  - split: test
    path: en-ku/test-*
  - split: train
    path: en-ku/train-*
  - split: validation
    path: en-ku/validation-*
- config_name: en-ky
  data_files:
  - split: test
    path: en-ky/test-*
  - split: train
    path: en-ky/train-*
  - split: validation
    path: en-ky/validation-*
- config_name: en-li
  data_files:
  - split: test
    path: en-li/test-*
  - split: train
    path: en-li/train-*
  - split: validation
    path: en-li/validation-*
- config_name: en-lt
  data_files:
  - split: test
    path: en-lt/test-*
  - split: train
    path: en-lt/train-*
  - split: validation
    path: en-lt/validation-*
- config_name: en-lv
  data_files:
  - split: test
    path: en-lv/test-*
  - split: train
    path: en-lv/train-*
  - split: validation
    path: en-lv/validation-*
- config_name: en-mg
  data_files:
  - split: test
    path: en-mg/test-*
  - split: train
    path: en-mg/train-*
  - split: validation
    path: en-mg/validation-*
- config_name: en-mk
  data_files:
  - split: test
    path: en-mk/test-*
  - split: train
    path: en-mk/train-*
  - split: validation
    path: en-mk/validation-*
- config_name: en-ml
  data_files:
  - split: test
    path: en-ml/test-*
  - split: train
    path: en-ml/train-*
  - split: validation
    path: en-ml/validation-*
- config_name: en-mn
  data_files:
  - split: train
    path: en-mn/train-*
- config_name: en-mr
  data_files:
  - split: test
    path: en-mr/test-*
  - split: train
    path: en-mr/train-*
  - split: validation
    path: en-mr/validation-*
- config_name: en-ms
  data_files:
  - split: test
    path: en-ms/test-*
  - split: train
    path: en-ms/train-*
  - split: validation
    path: en-ms/validation-*
- config_name: en-mt
  data_files:
  - split: test
    path: en-mt/test-*
  - split: train
    path: en-mt/train-*
  - split: validation
    path: en-mt/validation-*
- config_name: en-my
  data_files:
  - split: test
    path: en-my/test-*
  - split: train
    path: en-my/train-*
  - split: validation
    path: en-my/validation-*
- config_name: en-nb
  data_files:
  - split: test
    path: en-nb/test-*
  - split: train
    path: en-nb/train-*
  - split: validation
    path: en-nb/validation-*
- config_name: en-ne
  data_files:
  - split: test
    path: en-ne/test-*
  - split: train
    path: en-ne/train-*
  - split: validation
    path: en-ne/validation-*
- config_name: en-nl
  data_files:
  - split: test
    path: en-nl/test-*
  - split: train
    path: en-nl/train-*
  - split: validation
    path: en-nl/validation-*
- config_name: en-nn
  data_files:
  - split: test
    path: en-nn/test-*
  - split: train
    path: en-nn/train-*
  - split: validation
    path: en-nn/validation-*
- config_name: en-no
  data_files:
  - split: test
    path: en-no/test-*
  - split: train
    path: en-no/train-*
  - split: validation
    path: en-no/validation-*
- config_name: en-oc
  data_files:
  - split: test
    path: en-oc/test-*
  - split: train
    path: en-oc/train-*
  - split: validation
    path: en-oc/validation-*
- config_name: en-or
  data_files:
  - split: test
    path: en-or/test-*
  - split: train
    path: en-or/train-*
  - split: validation
    path: en-or/validation-*
- config_name: en-pa
  data_files:
  - split: test
    path: en-pa/test-*
  - split: train
    path: en-pa/train-*
  - split: validation
    path: en-pa/validation-*
- config_name: en-pl
  data_files:
  - split: test
    path: en-pl/test-*
  - split: train
    path: en-pl/train-*
  - split: validation
    path: en-pl/validation-*
- config_name: en-ps
  data_files:
  - split: test
    path: en-ps/test-*
  - split: train
    path: en-ps/train-*
  - split: validation
    path: en-ps/validation-*
- config_name: en-pt
  data_files:
  - split: test
    path: en-pt/test-*
  - split: train
    path: en-pt/train-*
  - split: validation
    path: en-pt/validation-*
- config_name: en-ro
  data_files:
  - split: test
    path: en-ro/test-*
  - split: train
    path: en-ro/train-*
  - split: validation
    path: en-ro/validation-*
- config_name: en-ru
  data_files:
  - split: test
    path: en-ru/test-*
  - split: train
    path: en-ru/train-*
  - split: validation
    path: en-ru/validation-*
- config_name: en-rw
  data_files:
  - split: test
    path: en-rw/test-*
  - split: train
    path: en-rw/train-*
  - split: validation
    path: en-rw/validation-*
- config_name: en-se
  data_files:
  - split: test
    path: en-se/test-*
  - split: train
    path: en-se/train-*
  - split: validation
    path: en-se/validation-*
- config_name: en-sh
  data_files:
  - split: test
    path: en-sh/test-*
  - split: train
    path: en-sh/train-*
  - split: validation
    path: en-sh/validation-*
- config_name: en-si
  data_files:
  - split: test
    path: en-si/test-*
  - split: train
    path: en-si/train-*
  - split: validation
    path: en-si/validation-*
- config_name: en-sk
  data_files:
  - split: test
    path: en-sk/test-*
  - split: train
    path: en-sk/train-*
  - split: validation
    path: en-sk/validation-*
- config_name: en-sl
  data_files:
  - split: test
    path: en-sl/test-*
  - split: train
    path: en-sl/train-*
  - split: validation
    path: en-sl/validation-*
- config_name: en-sq
  data_files:
  - split: test
    path: en-sq/test-*
  - split: train
    path: en-sq/train-*
  - split: validation
    path: en-sq/validation-*
- config_name: en-sr
  data_files:
  - split: test
    path: en-sr/test-*
  - split: train
    path: en-sr/train-*
  - split: validation
    path: en-sr/validation-*
- config_name: en-sv
  data_files:
  - split: test
    path: en-sv/test-*
  - split: train
    path: en-sv/train-*
  - split: validation
    path: en-sv/validation-*
- config_name: en-ta
  data_files:
  - split: test
    path: en-ta/test-*
  - split: train
    path: en-ta/train-*
  - split: validation
    path: en-ta/validation-*
- config_name: en-te
  data_files:
  - split: test
    path: en-te/test-*
  - split: train
    path: en-te/train-*
  - split: validation
    path: en-te/validation-*
- config_name: en-tg
  data_files:
  - split: test
    path: en-tg/test-*
  - split: train
    path: en-tg/train-*
  - split: validation
    path: en-tg/validation-*
- config_name: en-th
  data_files:
  - split: test
    path: en-th/test-*
  - split: train
    path: en-th/train-*
  - split: validation
    path: en-th/validation-*
- config_name: en-tk
  data_files:
  - split: test
    path: en-tk/test-*
  - split: train
    path: en-tk/train-*
  - split: validation
    path: en-tk/validation-*
- config_name: en-tr
  data_files:
  - split: test
    path: en-tr/test-*
  - split: train
    path: en-tr/train-*
  - split: validation
    path: en-tr/validation-*
- config_name: en-tt
  data_files:
  - split: test
    path: en-tt/test-*
  - split: train
    path: en-tt/train-*
  - split: validation
    path: en-tt/validation-*
- config_name: en-ug
  data_files:
  - split: test
    path: en-ug/test-*
  - split: train
    path: en-ug/train-*
  - split: validation
    path: en-ug/validation-*
- config_name: en-uk
  data_files:
  - split: test
    path: en-uk/test-*
  - split: train
    path: en-uk/train-*
  - split: validation
    path: en-uk/validation-*
- config_name: en-ur
  data_files:
  - split: test
    path: en-ur/test-*
  - split: train
    path: en-ur/train-*
  - split: validation
    path: en-ur/validation-*
- config_name: en-uz
  data_files:
  - split: test
    path: en-uz/test-*
  - split: train
    path: en-uz/train-*
  - split: validation
    path: en-uz/validation-*
- config_name: en-vi
  data_files:
  - split: test
    path: en-vi/test-*
  - split: train
    path: en-vi/train-*
  - split: validation
    path: en-vi/validation-*
- config_name: en-wa
  data_files:
  - split: test
    path: en-wa/test-*
  - split: train
    path: en-wa/train-*
  - split: validation
    path: en-wa/validation-*
- config_name: en-xh
  data_files:
  - split: test
    path: en-xh/test-*
  - split: train
    path: en-xh/train-*
  - split: validation
    path: en-xh/validation-*
- config_name: en-yi
  data_files:
  - split: test
    path: en-yi/test-*
  - split: train
    path: en-yi/train-*
  - split: validation
    path: en-yi/validation-*
- config_name: en-yo
  data_files:
  - split: train
    path: en-yo/train-*
- config_name: en-zh
  data_files:
  - split: test
    path: en-zh/test-*
  - split: train
    path: en-zh/train-*
  - split: validation
    path: en-zh/validation-*
- config_name: en-zu
  data_files:
  - split: test
    path: en-zu/test-*
  - split: train
    path: en-zu/train-*
  - split: validation
    path: en-zu/validation-*
- config_name: fr-nl
  data_files:
  - split: test
    path: fr-nl/test-*
- config_name: fr-ru
  data_files:
  - split: test
    path: fr-ru/test-*
- config_name: fr-zh
  data_files:
  - split: test
    path: fr-zh/test-*
- config_name: nl-ru
  data_files:
  - split: test
    path: nl-ru/test-*
- config_name: nl-zh
  data_files:
  - split: test
    path: nl-zh/test-*
- config_name: ru-zh
  data_files:
  - split: test
    path: ru-zh/test-*
---

# Dataset Card for OPUS-100

## Table of Contents
- [Dataset Description](#dataset-description)
  - [Dataset Summary](#dataset-summary)
  - [Supported Tasks and Leaderboards](#supported-tasks-and-leaderboards)
  - [Languages](#languages)
- [Dataset Structure](#dataset-structure)
  - [Data Instances](#data-instances)
  - [Data Fields](#data-fields)
  - [Data Splits](#data-splits)
- [Dataset Creation](#dataset-creation)
  - [Curation Rationale](#curation-rationale)
  - [Source Data](#source-data)
  - [Annotations](#annotations)
  - [Personal and Sensitive Information](#personal-and-sensitive-information)
- [Considerations for Using the Data](#considerations-for-using-the-data)
  - [Social Impact of Dataset](#social-impact-of-dataset)
  - [Discussion of Biases](#discussion-of-biases)
  - [Other Known Limitations](#other-known-limitations)
- [Additional Information](#additional-information)
  - [Dataset Curators](#dataset-curators)
  - [Licensing Information](#licensing-information)
  - [Citation Information](#citation-information)
  - [Contributions](#contributions)

## Dataset Description

- **Homepage:** https://opus.nlpl.eu/OPUS-100
- **Repository:** https://github.com/EdinburghNLP/opus-100-corpus
- **Paper:** https://arxiv.org/abs/2004.11867
- **Paper:** https://aclanthology.org/L10-1473/
- **Leaderboard:** [More Information Needed](https://github.com/huggingface/datasets/blob/master/CONTRIBUTING.md#how-to-contribute-to-the-dataset-cards)
- **Point of Contact:** [More Information Needed](https://github.com/huggingface/datasets/blob/master/CONTRIBUTING.md#how-to-contribute-to-the-dataset-cards)

### Dataset Summary

OPUS-100 is an English-centric multilingual corpus covering 100 languages.

OPUS-100 is English-centric, meaning that all training pairs include English on either the source or target side. The corpus covers 100 languages (including English).
The languages were selected based on the volume of parallel data available in OPUS.

### Supported Tasks and Leaderboards

Translation.

### Languages

OPUS-100 contains approximately 55M sentence pairs. Of the 99 language pairs, 44 have 1M sentence pairs of training data, 73 have at least 100k, and 95 have at least 10k.

## Dataset Structure

### Data Instances

```
{
  "translation": {
    "ca": "El departament de bombers té el seu propi equip d'investigació.",
    "en": "Well, the fire department has its own investigative unit."
  }
}
```

### Data Fields

- `translation` (`dict`): Parallel sentences for the pair of languages.

### Data Splits

The dataset is split into training, development, and test portions. Data was prepared by randomly sampled up to 1M sentence pairs per language pair for training and up to 2000 each for development and test. To ensure that there was no overlap (at the monolingual sentence level) between the training and development/test data, they applied a filter during sampling to exclude sentences that had already been sampled. Note that this was done cross-lingually so that, for instance, an English sentence in the Portuguese-English portion of the training data could not occur in the Hindi-English test set.

## Dataset Creation

### Curation Rationale

[More Information Needed]

### Source Data

[More Information Needed]

#### Initial Data Collection and Normalization

[More Information Needed]

#### Who are the source language producers?

[More Information Needed]

### Annotations

#### Annotation process

[More Information Needed]

#### Who are the annotators?

[More Information Needed]

### Personal and Sensitive Information

[More Information Needed]

## Considerations for Using the Data

### Social Impact of Dataset

[More Information Needed]

### Discussion of Biases

[More Information Needed]

### Other Known Limitations

[More Information Needed]

## Additional Information

### Dataset Curators

[More Information Needed]

### Licensing Information

[More Information Needed]

### Citation Information

If you use this corpus, please cite the paper:
```bibtex
@inproceedings{zhang-etal-2020-improving,
    title = "Improving Massively Multilingual Neural Machine Translation and Zero-Shot Translation",
    author = "Zhang, Biao  and
      Williams, Philip  and
      Titov, Ivan  and
      Sennrich, Rico",
    editor = "Jurafsky, Dan  and
      Chai, Joyce  and
      Schluter, Natalie  and
      Tetreault, Joel",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2020.acl-main.148",
    doi = "10.18653/v1/2020.acl-main.148",
    pages = "1628--1639",
}
```
and, please, also acknowledge OPUS:
```bibtex
@inproceedings{tiedemann-2012-parallel,
    title = "Parallel Data, Tools and Interfaces in {OPUS}",
    author = {Tiedemann, J{\"o}rg},
    editor = "Calzolari, Nicoletta  and
      Choukri, Khalid  and
      Declerck, Thierry  and
      Do{\u{g}}an, Mehmet U{\u{g}}ur  and
      Maegaard, Bente  and
      Mariani, Joseph  and
      Moreno, Asuncion  and
      Odijk, Jan  and
      Piperidis, Stelios",
    booktitle = "Proceedings of the Eighth International Conference on Language Resources and Evaluation ({LREC}'12)",
    month = may,
    year = "2012",
    address = "Istanbul, Turkey",
    publisher = "European Language Resources Association (ELRA)",
    url = "http://www.lrec-conf.org/proceedings/lrec2012/pdf/463_Paper.pdf",
    pages = "2214--2218",
}
```

### Contributions

Thanks to [@vasudevgupta7](https://github.com/vasudevgupta7) for adding this dataset.