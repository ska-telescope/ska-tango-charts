Helm Charts available on ska-tango-charts repository
====================================================

There are two helm charts available on this repository: one is called ``ska-tango-base`` and the other is the ``ska-tango-util``.
There is another helm chart, called ``ska-tango-umbrella``, which is used only for testing purposes.

The ska-tango-base helm chart
-------------------------

The ``ska-tango-base`` helm chart is an application chart which defines the basic TANGO ecosystem in kubernetes.

In specific it defines the following k8s services:
 - tangodb: it is a mysql database used to store configuration data used at startup of a device server (more information can be found `here <https://tango-controls.readthedocs.io/en/latest/reference/glossary.html#term-tango-database>`__. If the ``global.operator`` is true then this won't be generated in favour of a databaseds resource type. More information available `here <https://gitlab.com/ska-telescope/ska-tango-operator>`_
 - databaseds: it is a device server providing configuration information to all other components of the system as well as a runtime catalog of the components/devices (more information can be found `here <https://tango-controls.readthedocs.io/en/latest/reference/glossary.html#term-tango-host>`__.
 - itango: it is an interactive Tango client (more information can be found `here <https://gitlab.com/tango-controls/itango>`__.
 - vnc: it is a debian environment with x11 server and vnc/novnc installed on it (deprecated).
 - tangotest: it is the tango test device server (more information can be found `here <https://gitlab.com/tango-controls/TangoTest>`__.


The ska-tango-util helm chart
-------------------------

The ``ska-tango-util`` helm chart is a library chart which helps other application chart defines TANGO device servers.

In specific it defines the following helm named template:
 - configuration (deprecated): it creates a k8s service account, a role and role binding for waiting the configuration job to be done and a job for the `dsconfig <https://github.com/MaxIV-KitsControls/lib-maxiv-dsconfig>`_ application to apply a configuration json file set into the values file;
 - deviceserver (deprecated): it creates a k8s service and a k8s statefulset for a instance of a device server;
 - multidevice-config: it creates a ConfigMap which contains the generated `dsconfig <https://github.com/MaxIV-KitsControls/lib-maxiv-dsconfig>`_ json configuration file, the boostrap script for the `dsconfig <https://github.com/MaxIV-KitsControls/lib-maxiv-dsconfig>`_ application and a python script for multi class device server startup; if the ``global.operator`` is true then this won't be generated. More information available `here <https://gitlab.com/ska-telescope/ska-tango-operator>`_;
 - multidevice-job: it creates a job for the `dsconfig <https://github.com/MaxIV-KitsControls/lib-maxiv-dsconfig>`_ application to apply a configuration json file set into the values file; if the ``global.operator`` is true then this won't be generated. More information available `here <https://gitlab.com/ska-telescope/ska-tango-operator>`_;
 - multidevice-sacc-role: it creates a k8s service account, a role and role binding for waiting the configuration job to be done; if the ``global.operator`` is true then this won't be generated. More information available `here <https://gitlab.com/ska-telescope/ska-tango-operator>`_;
 - multidevice-svc: it creates a k8s service and a k8s statefulset for a device server tag specified in the values file. If the ``global.operator`` is true then this won't be generated in favour of a DeviceServer k8s type. More information available `here <https://gitlab.com/ska-telescope/ska-tango-operator>`_
 - deviceserver-pvc: it optionally creates a volume for the deviceserver when it contains the dictionary `volume`. The subkeys are `name`, `mountPath` and `storage`. See example below.
 - operator: it creates a k8s DeviceServer type of k8s resources. 
 - secret-provider-class: it creates a storage provider class for accessing vault secrets with the `csi provider <https://developer.hashicorp.com/vault/docs/platform/k8s/csi>`_. 

With the introduction of the `SKA TANGO Operator k8s controller <https://gitlab.com/ska-telescope/ska-tango-operator>`_ the library is also able to generate DeviceServer type of resources. This can be activate by setting the parameter ``global.operator``.

Device Server generation
++++++++++++++++++++++++

`Dsconfig <https://github.com/MaxIV-KitsControls/lib-maxiv-dsconfig>`_ is an application which configure the tango database with the help of a json file.
With ska-tango-util a device derver is configurable using specifications in a values.yaml file of the chart instead of the dsconfig.json file, where all device servers have a configuration yaml block.
Below there is an example of a values file that can be used with the ska-tango-util multi device definition:

.. code-block:: console

    deviceServers:
        theexample:
            name: "theexample-{{.Release.Name}}"
            function: ska-tango-example-powersupply
            domain: ska-tango-example
            instances: ["test"]
            polling: 1000
            entrypoints:
                - name: "powersupply.PowerSupply"
                path: "/app/module_example/powersupply.py"
                - name: "EventReceiver.EventReceiver"
                path: "/app/module_example/EventReceiver.py"
                - name: "Motor.Motor"
                path: "/app/module_example/Motor.py"
            server:
                name: "theexample"
                instances:
                - name: "test2"
                    classes:
                    - name: "PowerSupply"
                    devices:
                    - name: "test/power_supply/2"
                        properties:
                        - name: "test"
                        values:
                        - "test2"
                - name: "test"
                    classes:
                    - name: "PowerSupply"
                    devices:
                    - name: "test/power_supply/1"
                        properties:
                        - name: "test"
                        values:
                        - "test2"
                    - name: "EventReceiver"
                    devices:
                    - name: "test/eventreceiver/1"
                    - name: "Motor"
                    devices:
                    - name: "test/motor/1"
                        properties:
                        - name: "polled_attr"
                        values:
                        - "PerformanceValue"
                        - "{{ .Values.deviceServers.theexample.polling }}"
                        attribute_properties:
                        - attribute: "PerformanceValue"
                        properties:
                        - name: "rel_change"
                            values:
                            - "-1"
                            - "1"
            class_properties:
                - name: "PowerSupply"
                properties:
                    - name: "aClassProperty"
                    values: ["67.4", "123"]
                    - name: "anotherClassProperty"
                    values: ["test", "test2"]
            depends_on:
                - device: sys/database/2
            image:
                registry: "{{.Values.tango_example.image.registry}}"
                image: "{{.Values.tango_example.image.image}}"
                tag: "{{.Values.tango_example.image.tag}}"
                pullPolicy: "{{.Values.tango_example.image.pullPolicy}}"
            volume:
                name: firmware
                mountPath: /firmware
            postStart: "tango_admin --add-property test/motor/1 'LibConfig' 'user=xxx,password='$TEST"
            preStop: "tango_admin --delete-property test/motor/1 'LibConfig'"
            secretsInjectPath: /mnt/secrets-store
            secrets:
            - secretPath: kv/data/groups/ska-dev/system
              env:
                secretKey: test-injection
                envName: TEST
                default: "minikube-case"
            extraVolumes:
            - name: generic-volume
              persistentVolumeClaim: 
                claimName:  {{ .Release.Name }}-generic-pvc
            extraVolumeMounts:
            - name: generic-volume
              mountPath: /generic-volume

The most important fields are the following:
 - **deviceServers** : contains a list of all device server defined
 - **instances** : On this field the user can define which of the instances defined in the server tag are going to be created on the deviceServer.
 - **entrypoints** : The number of entrypoints should correspond to the defined in the server tag field.

    - **name** : This is a **mandatory** field at entrypoints. The name field has to have a format like NameOfTheModule.NameOfTheClass.
    - **path** : This is a **optional** field at entrypoints. The path field is the path of the module that has the class of the device. This field may not be present **only** if the module is included in the list of directories that the interpreter will search, one example is if the modules are installed with pip.

 - **server** : It's the equivalent of the dsconfig json file and define everything needed for a device server.

    - **intances** : A list of all instances for a device server. For each instance a number of devices can be defined together with the relative properties.
 - **class_properties** : On this field you can list your class properties.
 - **secretsInjectPath**: Path to be mount in the device server containing all secrets. 
 - **secrets**: On this field you can list your secret available in vault. The vault address should be specified in the chart values file `vaultAddress` or in global parameter called `global.vaultAddress`:
   - **secretPath**: path in vault.
   - **envName**: environment variable name to be set in the device server.
   - **default**: environment variable value to be set in minikube (when vault is not available).
 - **postStart/preStop**: On this field you can set the container lifecycle hooks as described `here <https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/>`__.
 - **extraVolumes**: On this field you can set any extra volume for the device server.
 - **extraVolumeMounts**: On this field you can set any extra volume mounts for the device server.

The device server configuration, like the above one, needs to be added to the values.yaml file. Below there is an example of how to add it (by splitting the definitions in different files):

.. code-block:: console

    deviceServers:
        theexample:
            instances: ["test2"]
            polling: 1000
            file: "data/theexample.yaml"

Fields explained:
    - **file** : This field specifies the path of the device server configuration block as shown above. Note:. This file should be included in a `data folder <https://gitlab.com/ska-telescope/ska-tango-example/-/tree/master/charts/ska-tango-example/data>`__ inside the chart.
    - **polling** : This field is referenced in the above device server configuration block. In fact the ska-tango-util device server definition template some of the field composing it (like the properties). In the above example the *polled_attr* property of the *test/motor/1* device takes its value from this field. As a consequence, this field allows us to change the value of the *polled_attr* property in the parent chart.
    - **instances** : If **instances** has values ​​in the value file, this takes precedence over the data file **instances** field.

The use of the yaml file allows users to have a cleaner and more understandable view of the DeviceServer configurations compared to a json file configuration.
The helm template multidevice-config creates a ConfigMap which contains the generated dsconfig that was loaded and converted to a json type file from the values.yaml file described above.


How to use the defined helm named template
++++++++++++++++++++++++++++++++++++++++++

A example on how to set up your k8s namespace with the helm named templates, described in the beginning of this `section <#the-ska-tango-util-helm-chart>`_, can be seen on `ska-tango-example <https://gitlab.com/ska-telescope/ska-tango-example>`_ repository.
This templates are called by the below `template <https://gitlab.com/ska-telescope/ska-tango-example/-/blob/master/charts/ska-tango-example/templates/deviceservers.yaml>`_ present on the ska-tango-example repository:

.. code-block:: console
    :linenos:

    {{ $localchart := . }}

    {{- range $key, $deviceserver := .Values.deviceServers }}

    {{- if hasKey $deviceserver "file"}}

    {{- $filedeviceserver := $.Files.Get $deviceserver.file | fromYaml }}
    {{- $_ := set $filedeviceserver "instances" (coalesce $localchart.Values.global.instances $deviceserver.instances $filedeviceserver.instances) }}
    {{- $context := dict "name" $key "deviceserver" $filedeviceserver "image" $deviceserver.image "local" $localchart }}
    {{ template "ska-tango-util.multidevice-config.tpl" $context }}
    {{ template "ska-tango-util.multidevice-sacc-role.tpl" $context }}
    {{ template "ska-tango-util.multidevice-job.tpl" $context }}
    {{ template "ska-tango-util.multidevice-svc.tpl" $context }}
    {{- $volume_context := dict "volume" $filedeviceserver.volume "local" $localchart }}
    {{ template "ska-tango-util.deviceserver-pvc.tpl" $volume_context }}

    {{- else }}

    {{- $_ := set $deviceserver "instances" (coalesce $localchart.Values.global.instances $deviceserver.instances) }}
    {{- $context := dict "name" $key "deviceserver" $deviceserver "image" $deviceserver.image "local" $localchart }}
    {{ template "ska-tango-util.multidevice-config.tpl" $context }}
    {{ template "ska-tango-util.multidevice-sacc-role.tpl" $context }}
    {{ template "ska-tango-util.multidevice-job.tpl" $context }}
    {{ template "ska-tango-util.multidevice-svc.tpl" $context }}
    {{- $volume_context := dict "volume" $deviceserver.volume "local" $localchart }}
    {{ template "ska-tango-util.deviceserver-pvc.tpl" $volume_context }}


    {{- end }}

    {{- end }} # deviceservers

Tango-example template description:
    - **Line 3**  to **Line 29** : This template will iterate through each field under deviceServers on the values.yaml file.
    - **Line 5**  to **Line 15** : If the device server has a file field we will get that configuration file and use it. (**Best Practice**: Add the deviceServer configuration in the data folder and then pass the path of it in the file field of the deviceServer).
    - **Line 17** to **Line 26** : If there is no file field it means that the configuration of this device was done inside the value.yaml. (**Note:** Making the configuration of the device inside the values.yaml makes this file bigger becoming harder to read and understand)
    - **Line 7**  : As discussed before it is possible to have a instances field in the values.yaml file and in the data file, it is also possible to have instances defined as a global field. It is being used a coalesced function that takes the first not null value of the list. The priority is, first it takes the instance value from the global variable if there is none it takes it from the values file and then from the data file.
    - **Line 19** : Same as line 8 but without the possibility of having the instance field on the data file.
    - **Line 9** and **Line 20** : Context is a list of variables that will passed as arguments to the templates.
    - **Line 14** to **Line 15**: Use and set the context for persistent volume claims attached to teh deviceserver
    - **Line 25** to **Line 26**: same as 14 to 15
    - **Templates** : There are five templates already described before. Each template will be called for each deviceServer as they are inside the range loop (line 3).
