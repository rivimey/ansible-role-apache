# Ansible Role: Apache 2.x

[![CI](https://github.com/geerlingguy/ansible-role-apache/workflows/CI/badge.svg?event=push)](https://github.com/geerlingguy/ansible-role-apache/actions?query=workflow%3ACI)

An Ansible Role that installs Apache 2.x on RHEL/CentOS, Debian/Ubuntu, SLES and Solaris.

## Requirements

If you are using SSL/TLS, you will need to provide your own certificate and key files. You can generate a self-signed certificate with a command like `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout example.key -out example.crt`.

If you are using Apache with PHP, I recommend using the `geerlingguy.php` role to install PHP, and you can either use mod_php (by adding the proper package, e.g. `libapache2-mod-php5` for Ubuntu, to `php_packages`), or by also using `geerlingguy.apache-php-fpm` to connect Apache to PHP via FPM. See that role's README for more info.

## Role Global Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

    apache_enablerepo: ""

The repository to use when installing Apache (only used on RHEL/CentOS systems). If you'd like later versions of Apache than are available in the OS's core repositories, use a repository like EPEL (which can be installed with the `geerlingguy.repo-epel` role).

    apache_listen_ip: "*"
    apache_listen_port: 80
    apache_listen_port_ssl: 443

The IP address and ports on which apache should be listening. Useful if you have another service (like a reverse proxy) listening on port 80 or 443 and need to change the defaults.

    apache_create_vhosts: true
    apache_vhosts_filename: "vhosts.conf"
    apache_vhosts_template: "vhosts.conf.j2"

If set to true, a vhosts file, managed by this role's variables (see below), will be created and placed in the Apache configuration folder. If set to false, you can place your own vhosts file into Apache's configuration folder and skip the convenient (but more basic) one added by this role. You can also override the template used and set a path to your own template, if you need to further customize the layout of your VirtualHosts.

    apache_remove_default_vhost: false

On Debian/Ubuntu, a default virtualhost is included in Apache's configuration. Set this to `true` to remove that default virtualhost configuration file.

    apache_global_vhost_settings: |
      DirectoryIndex index.php index.html
      # Add other global settings on subsequent lines.

## Virtual Host Variables

You can add or override global Apache configuration settings in the role-provided vhosts file (assuming `apache_create_vhosts` is true) using this variable. By default it only sets the DirectoryIndex configuration.

    apache_vhosts:
      # Additional optional properties: 'serveradmin, serveralias, extra_parameters'.
      - servername: "local.dev"
        documentroot: "/var/www/html"

Add a set of properties per virtualhost, including `servername` (required), `documentroot` (required), `allow_override` (optional: defaults to the value of `apache_allow_override`), `options` (optional: defaults to the value of `apache_options`), `serveradmin` (optional), `serveralias` (optional) and `extra_parameters` (optional: you can add whatever additional configuration lines you'd like in here).

Here's an example using `extra_parameters` to add a RewriteRule to redirect all requests to the `www.` site:

      - servername: "www.local.dev"
        serveralias: "local.dev"
        documentroot: "/var/www/html"
        extra_parameters: |
          RewriteCond %{HTTP_HOST} !^www\. [NC]
          RewriteRule ^(.*)$ http://www.%{HTTP_HOST}%{REQUEST_URI} [R=301,L]

The `|` denotes a multiline scalar block in YAML, so newlines are preserved in the resulting configuration file output.

    apache_vhosts_ssl: []

No SSL vhosts are configured by default, but you can add them using the same pattern as `apache_vhosts`, with a few additional directives, like the following example:

    apache_vhosts_ssl:
      - servername: "local.dev"
        documentroot: "/var/www/html"
        certificate_file: "/home/vagrant/example.crt"
        certificate_key_file: "/home/vagrant/example.key"
        certificate_chain_file: "/path/to/certificate_chain.crt"
        extra_parameters: |
          RewriteCond %{HTTP_HOST} !^www\. [NC]
          RewriteRule ^(.*)$ http://www.%{HTTP_HOST}%{REQUEST_URI} [R=301,L]

Other SSL directives can be managed with other SSL-related role variables.

    apache_ssl_protocol: "All -SSLv2 -SSLv3"
    apache_ssl_cipher_suite: "AES256+EECDH:AES256+EDH"

The SSL protocols and cipher suites that are used/allowed when clients make secure connections to your server. These are secure/sane defaults, but for maximum security, performand, and/or compatibility, you may need to adjust these settings.

    apache_allow_override: "All"
    apache_options: "-Indexes +FollowSymLinks"

The default values for the `AllowOverride` and `Options` directives for the `documentroot` directory of each vhost.  A vhost can overwrite these values by specifying `allow_override` or `options`.

    apache_mods_enabled:
      - rewrite
      - ssl
    apache_mods_disabled: []

Which Apache mods to enable or disable (these will be symlinked into the appropriate location). See the `mods-available` directory inside the apache configuration directory (`/etc/apache2/mods-available` on Debian/Ubuntu) for all the available mods.

    apache_packages:
      - [platform-specific]

The list of packages to be installed. This defaults to a set of platform-specific packages for RedHat or Debian-based systems (see `vars/RedHat.yml` and `vars/Debian.yml` for the default values).

    apache_state: started

Set initial Apache daemon state to be enforced when this role is run. This should generally remain `started`, but you can set it to `stopped` if you need to fix the Apache config during a playbook run or otherwise would not like Apache started at the time this role is run.

    apache_enabled: yes

Set the Apache service boot time status. This should generally remain `yes`, but you can set it to `no` if you need to run Ansible while leaving the service disabled.

    apache_packages_state: present

If you have enabled any additional repositories such as _ondrej/apache2_, [geerlingguy.repo-epel](https://github.com/geerlingguy/ansible-role-repo-epel), or [geerlingguy.repo-remi](https://github.com/geerlingguy/ansible-role-repo-remi), you may want an easy way to upgrade versions. You can set this to `latest` (combined with `apache_enablerepo` on RHEL) and can directly upgrade to a different Apache version from a different repo (instead of uninstalling and reinstalling Apache).

    apache_ignore_missing_ssl_certificate: true

If you would like to only create SSL vhosts when the vhost certificate is present (e.g. when using Let’s Encrypt), set `apache_ignore_missing_ssl_certificate` to `false`. When doing this, you might need to run your playbook more than once so all the vhosts are configured (if another part of the playbook generates the SSL certificates).

### Enable use of PHP-FPM for a Site

The vhost key `php_fpm` signals two things: that the server should configure the site to use PHP-FPM, and the version of php to configure. So:

      - servername: "www.example.uk"
        php_fpm: 8.1

would cause the server to enable php-fpm8.1 on the site and setting `index.php` as the DirectoryIndex.

It enables php-fpm by directly including the file `conf-available/php{{ vhost.php_fpm }}-fpm.conf` in the virtualhost, which as shipped by Debian, Ubuntu et enables the correct FCGI proxy details.

> The php-fpm apache conf should _not_ be enabled first (e.g. using `a2enconf php8.1-fpm`) as this would enable that configuration for all sites. By including the conf file within the Virtualhost it becomes possible to run two sites using different versions of php.

> Some php-fpm configuration files wrap the whole stanza in "if mod_php is not installed", so simply installing mod_php on the server will break the php-fpm configuration. As mod_php is noticeably slower than php-fpm, disabling and uninstalling mod_php should be the first path to exploree. 

> There could be a conflict between the global `php_version` variable, which is used by some php configuration roles, and the version specified here. You can of course specify this key using "{{ php_version }}", but if you chose not to, you will need to otherwise ensure the indicated php-fpm version is installed and operational. To aid you in this, the template vhosts configuration file includes both version numbers. 

### Server Status configuration

Those wanting to configure a tool such as prometheus to gather performance data about apache will likely wish to configure the `/server-status` endpoint & module. This is slightly complicated with vhosts because it requires a global and a local parameter. The vhost key:

      - servername: "www.example.uk"
        serverstatus: true
        status_url: "/-/serverstatus"

will do just that, in this case configuring the endpoint `http://servername/-/serverstatus}` on the server with local-only access. If the serverstatus key is missing or not True, the status url is explicitly denied.

Setting the vhost key `status_url` is optional and the default value is the same as the default for the mod_status module itself, "/server-status".

> Note: You must separately arrange for the mod_status apache module to be installed and enabled using the other tools in this role.

### Automatic Redirect to SSL host 

The (non-SSL) vhost key `redirectssl`  can be used to set up an HTTP host that redirects to the equivalently-named HTTPS host:

      - servername: "www.example.uk"
        serveralias: "example.uk"
        serveradmin: "postmaster@{{ primary_domain }}"
        redirectssl: yes

This will redirect `http://www.example.uk/foo` to `https://www.example.uk/foo` . 
and `http://example.uk/foo` to `https://www.example.uk/foo` without any further effort.

> Note: You must separately arrange for the mod_rewrite apache module to be installed and enabled using the other tools in this role.

### Configuring Drupal (& other CMS) Query URL Rewrites

The vhost key `is_drupal` can be used to signal that this is a Drupal site being served, one effect being the inclusion of Rewrite rules to transform `/path` into the usable `/index.php?q=/path` form. While this was designed for Drupal it is probably also usable by several other CMSs.

> Note: You must separately arrange for the mod_rewrite apache module to be installed and enabled using the other tools in this role.

### Configuring one or more Reverse Proxy(s)

Reverse proxies can be configured on a host using the vhost key `reverseproxy`, which is an array of proxy dictionaries:'

      - servername: "www.example.uk"
        reverseproxy:
            - dir: "/"
              url: "http://site.example.org:8888/"

Two additional keys can be added to 'dir' and 'url' to provide values for the ProxyPreserveHost and ProxyAddHeaders configuration keywords should they be needed, for example:

              preservehost: yes
              proxyheaders: no

Proxies set up using this have both ProxyPass and ProxyPassReverse set.

> Note: You must separately arrange for the mod_proxy apache module to be installed and enabled using the other tools in this role.

## .htaccess-based Basic Authorization

If you require Basic Auth support, you can add it either through a custom template, or by adding `extra_parameters` to a VirtualHost configuration, like so:

    extra_parameters: |
      <Directory "/var/www/password-protected-directory">
        Require valid-user
        AuthType Basic
        AuthName "Please authenticate"
        AuthUserFile /var/www/password-protected-directory/.htpasswd
      </Directory>

To password protect everything within a VirtualHost directive, use the `Location` block instead of `Directory`:

    <Location "/">
      Require valid-user
      ....
    </Location>

You would need to generate/upload your own `.htpasswd` file in your own playbook. There may be other roles that support this functionality in a more integrated way.

## Dependencies

None.

## Example Playbook

    - hosts: webservers
      vars_files:
        - vars/main.yml
      roles:
        - { role: geerlingguy.apache }

*Inside `vars/main.yml`*:

    apache_listen_port: 8080
    apache_vhosts:
      - {servername: "example.com", documentroot: "/var/www/vhosts/example_com"}

## License

MIT / BSD

## Author Information

This role was created in 2014 by [Jeff Geerling](https://www.jeffgeerling.com/), author of [Ansible for DevOps](https://www.ansiblefordevops.com/).
Extensions were added 2019-2023 by  [Ruth Ivimey-Cook](https://www.ivimey.com/). Updates from jeffgeerling's original have been included where possible.
