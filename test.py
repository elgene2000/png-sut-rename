power_type = "webhovok"
data = {
    "hostname": "new_name",
    **(
        {
            "power_parameters_power_on_uri": "http://png-dcgpuval-platypiserver.png.dcgpu/api/v1/asrock355x-png-5cr12-02b/power_on_pxe",
            "power_parameters_power_off_uri": "http://png-dcgpuval-platypiserver.png.dcgpu/api/v1/asrock355x-png-5cr12-02b/power_off_pxe",
            "power_parameters_power_query_uri": "http://png-dcgpuval-platypiserver.png.dcgpu/api/v1/asrock355x-png-5cr12-02b/power_check_pxe",
        }
        if power_type == "webhook"
        else {}
    ),
}

print(data)
