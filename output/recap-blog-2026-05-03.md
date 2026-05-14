_Questo recap è stato generato con gemini-3-flash-preview_

---
title: "Sotto il cofano: l'evoluzione tecnica di Pensieri in codice"
date: 2026-05-03T10:00:00+02:00
featureImage: https://cdn.pensieriincodice.it/images/blog/recap.png
image: images/blog/recap.png
tags:
- Dev
- Recap
categories:
- News
type: blog
author: Valerio Galano
---

Hai presente quella sensazione di quando inizi a sistemare un piccolo cassetto e finisci, quasi senza accorgertene, per traslocare l'intera casa? Ecco, gli ultimi mesi sul codice di Pensieri in codice sono stati esattamente così. Tutto è partito da un dettaglio del player audio sul sito e, commit dopo commit, mi sono ritrovato a riscrivere l'esperienza di ascolto e gran parte delle automazioni che ruotano attorno al podcast.

Il cuore di questo cambiamento è stato il repository https://github.com/valeriogalano/pensieriincodice-website. Volevo che il player non fosse solo un accessorio, ma uno strumento completo per chi, come te, dedica del tempo all'ascolto approfondito. Ho aggiunto i segnalibri per salvare i momenti salienti, lo sleep timer per chi si addormenta con le mie storie e la possibilità di condividere un episodio partendo da un secondo esatto. Ma non mi sono fermato alla superficie: ho lavorato duramente sulla sincronizzazione delle trascrizioni e sui gesti touch, trasformando il sito in una vera PWA che puoi installare sul telefono. 🎧

Un'altra scelta di cui vado fiero è stata quella di "tagliare i ponti" con l'esterno. Ho rimosso ogni dipendenza da CDN di terze parti e persino i Google Fonts, preferendo ospitare tutto localmente. È una questione di privacy, certo, ma anche di indipendenza e controllo sul mio piccolo angolo di web. Nel frattempo, ho continuato a nutrire il repository degli asset su https://github.com/valeriogalano/pensieriincodice-cdn, preparando il terreno per gli episodi 148 e 149 con nuove copertine e capitoli.

Poi c'è stata la grande migrazione. Ho deciso di abbandonare il PHP per tutte le mie automazioni social, riscrivendo i bot in Python. È stato un lavoro metodico che ha coinvolto https://github.com/valeriogalano/podcast-rss-to-telegram, Mastodon, LinkedIn e persino X. Ora tutto è più snello, modulare e soprattutto più facile da testare. In questo fermento è nato anche un esperimento divertente: un bot su https://github.com/valeriogalano/podcast-quiz-to-telegram che usa l'intelligenza artificiale per generare quiz basati sugli episodi del podcast. È un modo curioso per interagire con la community e vedere quanto siamo stati attenti durante l'ascolto. 🤖

Infine, ho dedicato molta energia a https://github.com/valeriogalano/podcast-audiogram-generator. L'ho praticamente rivoluzionato introducendo il rendering parallelo e la possibilità di generare audiogrammi per interi episodi, migliorando drasticamente la velocità di produzione dei contenuti video per i social.

Tutto questo lavoro mi ha portato a una riflessione che va oltre il codice. Spesso pensiamo che la tecnologia debba solo "funzionare", ma c'è una bellezza profonda nel prendersi cura dei dettagli, nel rendere un'interfaccia più fluida o un'automazione più resiliente. Curare il proprio software è come curare un giardino: non lo fai solo perché sia produttivo, ma perché quel processo di rifinitura costante è, in fondo, una forma di rispetto verso chi quel giardino lo visiterà. E spero che tu, navigando sul sito o ascoltando un episodio, possa percepire un po' di questa cura.