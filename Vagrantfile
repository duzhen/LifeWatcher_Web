# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

    config.vm.box = "ubuntu/xenial64"

    config.vm.define :devmachine do |node|
        node.vm.hostname = "devmachine"
        node.vm.network "private_network", ip: "192.168.33.20"
    end

    config.vm.provider "virtualbox" do |vb|
        vb.memory = "1024"
        vb.cpus = "2"
  end

    config.vm.provision "shell", inline: <<-SHELL
        echo "Installing docker engine...."
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        apt-get update
        apt-get install -y docker-ce
        sudo usermod -aG docker ubuntu

        echo "Installing python & development tools ..."
        sudo apt-get install -y python python-dev python-pip
        sudo pip install --upgrade pip
        sudo pip install --upgrade virtualenv

    SHELL

end
