// Registra o tráfego com o AK820 Pro: feature reports (ioctl) em qualquer
// interface e write/read só nas interfaces 2 e 3 (nunca a 0, que traz o que é digitado).
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <stdlib.h>
#include <pthread.h>
static pthread_mutex_t mx = PTHREAD_MUTEX_INITIALIZER;
static const char *alvos[4];
static int alvo(int fd){
    char l[64], p[256]; snprintf(l,sizeof l,"/proc/self/fd/%d",fd);
    ssize_t n=readlink(l,p,sizeof p-1); if(n<=0) return -1; p[n]=0;
    for(int i=0;i<4;i++) if(alvos[i] && !strcmp(p,alvos[i])) return i;
    return -1;
}
static void reg(const char *tipo,int iface,const unsigned char *b,size_t n){
    const char *arq=getenv("HIDLOG"); if(!arq) return;
    pthread_mutex_lock(&mx);
    FILE *f=fopen(arq,"a"); if(f){ struct timespec t; clock_gettime(CLOCK_REALTIME,&t);
      fprintf(f,"%ld.%06ld if%d %s %zu ",(long)t.tv_sec,t.tv_nsec/1000,iface,tipo,n);
      for(size_t i=0;i<n;i++) fprintf(f,"%02x",b[i]); fputc('\n',f); fclose(f);}
    pthread_mutex_unlock(&mx);
}
__attribute__((constructor)) static void ini(void){
    alvos[0]=getenv("HID_IF0"); alvos[1]=getenv("HID_IF1"); alvos[2]=getenv("HID_IF2"); alvos[3]=getenv("HID_IF3");
}
int ioctl(int fd, unsigned long req, ...){
    va_list ap; va_start(ap,req); void *arg=va_arg(ap,void*); va_end(ap);
    static int (*orig)(int,unsigned long,...); if(!orig) orig=dlsym(RTLD_NEXT,"ioctl");
    unsigned nr=req&0xff, tp=(req>>8)&0xff, sz=(req>>16)&0x3fff; int i=-1;
    if(tp=='H' && (nr==6||nr==7||nr==0x0b||nr==0x0c)) i=alvo(fd);
    if(i>=0 && (nr==6||nr==0x0b)) reg(nr==6?"SETF":"SETI",i,arg,sz);
    int r=orig(fd,req,arg);
    if(i>=0 && (nr==7||nr==0x0c)) reg(nr==7?"GETF":"GETI",i,arg,r>0?(size_t)r:0);
    return r;
}
ssize_t write(int fd,const void *b,size_t n){
    static ssize_t (*orig)(int,const void*,size_t); if(!orig) orig=dlsym(RTLD_NEXT,"write");
    int i=alvo(fd); if(i>=2) reg("OUT",i,b,n);
    return orig(fd,b,n);
}
ssize_t read(int fd,void *b,size_t n){
    static ssize_t (*orig)(int,void*,size_t); if(!orig) orig=dlsym(RTLD_NEXT,"read");
    ssize_t r=orig(fd,b,n); if(r>0){ int i=alvo(fd); if(i>=2) reg("IN",i,b,r);} return r;
}
