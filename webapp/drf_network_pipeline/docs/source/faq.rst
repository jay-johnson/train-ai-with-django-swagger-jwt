Frequently Asked Questions
==========================

What AntiNex is Not and Disclaimers
-----------------------------------

There's a lot of moving pieces in AI, and I wanted to be clear what is currently not supported:

#.  Custom layers or custom Deep Neural Network models - only Keras Sequential neural networks, KerasRegressor, KerasClassifier, Stratified Kfolds, cross validation scoring, Scalers, Add and Dropout are supported. PR's are always welcomed!
#.  Able to tell what your applications are doing today that is good, non-attack traffic out of the box. AntiNex requires recording how the network is being used in normal operation + identifying what you want to protect (do you want tcp traffic only? or a combination of tcp + udp + arp?). It uses the captured traffic to build the intial training dataset.
#.  Exotic attacks - The network pipeline includes the Zed Attack Proxy (ZED) for OWASP dynamic security analysis. This tool attacks using a fuzzing attack on web applications. ZED was used to generate the latest attack datasets, and there is no guarantee the latest dnn's will always be effective with attacks I have not seen yet. Please share your findings and reach out if you know how to generate new, better attack simulations to help us all. PR's are always welcomed!
#.  Image predictions and Convoluted Neural Networks - it's only works on numeric datasets.
#.  Recurrent Neural Networks - I plan on adding LTSM support into the antinex-utils, but the scores were already good enough to release this first build.
#.  Embedding Layers - I want to add payload deserialization to the packet processing with support for decrypting traffic, but the dnn scores were good enough to skip this feature for now.
#.  Adversarial Neural Networks - I plan on creating attack neural networks from the datasets to beat up the trained ones, but this is a 2.0 feature at this point.
#.  Saving models to disk is broken - I have commented out the code and found a keras issue that looks like the same problem I am hitting... I hope it is resovled so we can share model files via S3.

Why the name?
-------------

I was describing what this did and my sister-in-law said it reminded her of antivirus but for network defense. So instead of calling it **Anti-Network Exploits** it's just **AntiNex** or **anex** for short. Thanks Alli for the name!

