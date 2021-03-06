from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from project.models import ProjectStage
from .models import DeploymentInstance

import subprocess, shlex


# Create your views here.

@login_required
def deployments(request):
    """Show all deployments for the user"""
    deployments = DeploymentInstance.objects.filter(user=request.user)
    return render(request,'deployments.html', context = {'deployments':deployments})

@login_required
def deploy_results(request,uuid):
    """Taking the log file for the task and shows """
    deployment_instance = get_object_or_404(DeploymentInstance, id=uuid)

    try:
        with open(f'/tmp/{deployment_instance.id}.txt') as f:
            lines = f.readlines()
    except:
        print ('Unable to load log file')
        messages.error(request, 'Unable to load log file')
        return redirect('deployments')

    return render(request,'deploy_results.html',context = {'deployment_instance':deployment_instance,'out':lines})

@login_required
def deploy_project(request,id):
    """Get and post method, getting args and do the deployments"""
    project_stage = get_object_or_404(ProjectStage, id=id)
    if request.method == 'POST':
        branch= request.POST.get('branch', 'master')
        if project_stage.host == 'localhost':

            d_i = DeploymentInstance(project_stage=project_stage,user=request.user,status='p')
            d_i.save()
            print(d_i.id)
            print("running in local")
            my_cmd = f'bash {project_stage.script_location} {branch} {d_i.id}'
            print(my_cmd)
            args = shlex.split(my_cmd)
            subprocess.Popen(args)
            print("running in local")
            return redirect('deploy_results', uuid=d_i.id)

        else:
            # TODO:
            print("running in remote")
            print("ssh")
            p = subprocess.Popen(['cat', '/tmp/a.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            print(out,err)


        return render(request,'deploy.html', context = {})

    else:
        project = project_stage.project

        return render(request,'deploy.html', context = {'project_stage':project_stage})
